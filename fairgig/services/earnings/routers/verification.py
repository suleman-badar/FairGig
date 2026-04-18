from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.shift import Shift
from schemas.shift import ShiftOut, VerificationReviewRequest
from utils.dependencies import AuthUser, require_role

router = APIRouter(prefix="/verification", tags=["verification"])


@router.get("/queue")
def verification_queue(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_role("verifier", "advocate", "admin")),
):
    query = db.query(Shift).filter(Shift.verification_status == "pending")
    total = query.count()
    items = (
        query.order_by(Shift.screenshot_uploaded_at.asc().nullsfirst(), Shift.created_at.asc())
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


@router.post("/{shift_id}/review", response_model=ShiftOut)
def review_shift(
    shift_id: str,
    payload: VerificationReviewRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_role("verifier", "admin")),
):
    shift = db.query(Shift).filter(Shift.id == UUID(shift_id)).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    shift.verification_status = payload.status
    shift.verifier_note = payload.note
    shift.verifier_id = UUID(current_user.id)
    shift.verified_at = datetime.now(UTC)

    db.add(shift)
    db.commit()
    db.refresh(shift)
    return ShiftOut.model_validate(shift)
