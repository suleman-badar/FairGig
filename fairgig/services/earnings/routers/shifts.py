from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models.shift import Shift
from schemas.shift import BulkImportResponse, ShiftCreate, ShiftCreateResponse, ShiftOut, ShiftUpdate
from utils.csv_parser import parse_shift_csv
from utils.dependencies import AuthUser, get_current_user

router = APIRouter(prefix="/shifts", tags=["shifts"])


def _warn_if_mismatch(gross: float, deductions: float, net: float) -> str | None:
    expected = gross - deductions
    if abs(expected - net) > 1:
        return (
            f"Warning: reported net (Rs. {net:.2f}) differs from expected "
            f"(Rs. {expected:.2f}) by more than Rs. 1"
        )
    return None


@router.post("", response_model=ShiftCreateResponse)
def create_shift(
    payload: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    if current_user.role != "worker":
        raise HTTPException(status_code=403, detail="Only workers can create shifts")

    shift = Shift(
        worker_id=UUID(current_user.id),
        platform=payload.platform,
        shift_date=payload.shift_date,
        hours_worked=payload.hours_worked,
        gross_earned=payload.gross_earned,
        platform_deductions=payload.platform_deductions,
        net_received=payload.net_received,
        notes=payload.notes,
        verification_status="unsubmitted",
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    return ShiftCreateResponse(
        shift=ShiftOut.model_validate(shift),
        warning=_warn_if_mismatch(payload.gross_earned, payload.platform_deductions, payload.net_received),
    )


@router.get("")
def list_shifts(
    platform: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    verification_status: str | None = Query(default=None),
    worker_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    query = db.query(Shift)

    if current_user.role == "worker":
        query = query.filter(Shift.worker_id == UUID(current_user.id))
    elif worker_id:
        query = query.filter(Shift.worker_id == UUID(worker_id))

    if platform:
        query = query.filter(Shift.platform == platform)
    if from_date:
        query = query.filter(Shift.shift_date >= from_date)
    if to_date:
        query = query.filter(Shift.shift_date <= to_date)
    if verification_status:
        query = query.filter(Shift.verification_status == verification_status)

    total = query.count()
    items = (
        query.order_by(Shift.shift_date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "items": [ShiftOut.model_validate(item) for item in items],
        "page": page,
        "per_page": per_page,
        "total": total,
    }


@router.get("/{shift_id}", response_model=ShiftOut)
def get_shift(
    shift_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    shift = db.query(Shift).filter(Shift.id == UUID(shift_id)).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    if current_user.role == "worker" and str(shift.worker_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return ShiftOut.model_validate(shift)


@router.patch("/{shift_id}", response_model=ShiftOut)
def update_shift(
    shift_id: str,
    payload: ShiftUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    shift = db.query(Shift).filter(Shift.id == UUID(shift_id)).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    if current_user.role != "worker" or str(shift.worker_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if shift.verification_status == "verified":
        raise HTTPException(status_code=400, detail="Verified shifts cannot be edited")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(shift, key, value)

    db.add(shift)
    db.commit()
    db.refresh(shift)
    return ShiftOut.model_validate(shift)


@router.delete("/{shift_id}")
def delete_shift(
    shift_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    shift = db.query(Shift).filter(Shift.id == UUID(shift_id)).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    if current_user.role != "worker" or str(shift.worker_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if shift.verification_status == "verified":
        raise HTTPException(status_code=400, detail="Verified shifts cannot be deleted")

    db.delete(shift)
    db.commit()
    return {"detail": "Shift deleted"}


@router.post("/bulk", response_model=BulkImportResponse)
async def bulk_import_shifts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    if current_user.role != "worker":
        raise HTTPException(status_code=403, detail="Only workers can import shifts")

    content = await file.read()
    rows, errors = parse_shift_csv(content)
    inserted = 0

    for row in rows:
        try:
            shift = Shift(
                worker_id=UUID(current_user.id),
                platform=row.platform,
                shift_date=row.shift_date,
                hours_worked=row.hours_worked,
                gross_earned=row.gross_earned,
                platform_deductions=row.platform_deductions,
                net_received=row.net_received,
                notes=row.notes,
                verification_status="unsubmitted",
            )
            db.add(shift)
            inserted += 1
        except Exception as exc:
            errors.append({"row": "unknown", "reason": str(exc)})

    db.commit()
    return BulkImportResponse(inserted=inserted, errors=errors)
