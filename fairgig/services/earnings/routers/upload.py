import mimetypes
import os
import time
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.shift import Shift
from schemas.shift import ShiftOut
from utils.dependencies import AuthUser, get_current_user
from utils.file_store import get_screenshot_path, save_screenshot, validate_mime_type

router = APIRouter(tags=["upload"])
_UPLOAD_WINDOW_SECONDS = 60
_UPLOAD_LIMIT_PER_WINDOW = 20
_UPLOAD_BUCKETS: dict[str, list[float]] = {}


def _check_upload_rate_limit(user_id: str) -> None:
    now = time.time()
    bucket = _UPLOAD_BUCKETS.setdefault(user_id, [])
    bucket[:] = [ts for ts in bucket if now - ts <= _UPLOAD_WINDOW_SECONDS]
    if len(bucket) >= _UPLOAD_LIMIT_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Upload rate limit exceeded")
    bucket.append(now)


@router.post("/shifts/{shift_id}/screenshot", response_model=ShiftOut)
async def upload_screenshot(
    shift_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    if current_user.role != "worker":
        raise HTTPException(status_code=403, detail="Only workers can upload screenshots")

    shift = db.query(Shift).filter(Shift.id == UUID(shift_id)).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    if str(shift.worker_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not validate_mime_type(file.content_type or ""):
        raise HTTPException(
            status_code=400,
            detail="Unsupported MIME type. Allowed: image/jpeg, image/png, image/webp",
        )

    _check_upload_rate_limit(current_user.id)

    payload = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(payload) > max_bytes:
        raise HTTPException(status_code=400, detail="File too large")

    filename = save_screenshot(current_user.id, shift_id, payload, file.content_type or "image/jpeg")

    shift.screenshot_filename = filename
    shift.screenshot_uploaded_at = datetime.now(UTC)
    shift.verification_status = "pending"
    db.add(shift)
    db.commit()
    db.refresh(shift)

    return ShiftOut.model_validate(shift)


@router.get("/shifts/{shift_id}/screenshot")
def get_screenshot(
    shift_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
):
    shift = db.query(Shift).filter(Shift.id == UUID(shift_id)).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    if current_user.role == "worker" and str(shift.worker_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if current_user.role not in {"worker", "verifier", "advocate", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not shift.screenshot_filename:
        raise HTTPException(status_code=404, detail="No screenshot uploaded")

    abs_path = get_screenshot_path(shift.screenshot_filename)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Screenshot file not found")

    mime, _ = mimetypes.guess_type(abs_path)
    return FileResponse(abs_path, media_type=mime or "application/octet-stream")
