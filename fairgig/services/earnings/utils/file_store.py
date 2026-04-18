import os
from datetime import UTC, datetime

from config import settings


def validate_mime_type(content_type: str) -> bool:
    allowed = {mime.strip() for mime in settings.allowed_mime_types.split(",") if mime.strip()}
    return content_type in allowed


def save_screenshot(worker_id: str, shift_id: str, file_bytes: bytes, mime_type: str) -> str:
    ext = ".jpg"
    if mime_type == "image/png":
        ext = ".png"
    elif mime_type == "image/webp":
        ext = ".webp"

    worker_dir = os.path.join(settings.upload_dir, worker_id)
    os.makedirs(worker_dir, exist_ok=True)

    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    filename = f"{shift_id}_{ts}{ext}"
    abs_path = os.path.join(worker_dir, filename)

    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    return os.path.relpath(abs_path, settings.upload_dir)


def get_screenshot_path(filename: str) -> str:
    return os.path.join(settings.upload_dir, filename)
