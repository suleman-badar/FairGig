import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import RefreshToken, User
from schemas.user import (
    LoginRequest,
    MeUpdateRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from utils.dependencies import get_current_user
from utils.jwt import create_access_token
from utils.password import hash_password, verify_password

router = APIRouter(tags=["auth"])
limiter = Limiter(key_func=lambda request: request.client.host if request.client else "unknown")


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _issue_refresh_token(user_id: str, db: Session) -> str:
    raw = secrets.token_urlsafe(48)
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=_hash_refresh_token(raw),
        expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days),
    )
    db.add(db_token)
    db.commit()
    return raw


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        phone=user.phone,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        city_zone=user.city_zone,
        worker_category=user.worker_category,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")

    user = User(
        phone=payload.phone,
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        city_zone=payload.city_zone,
        worker_category=payload.worker_category,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_user_out(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = _issue_refresh_token(str(user.id), db)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=_to_user_out(user),
    )


@router.post("/refresh")
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = _hash_refresh_token(payload.refresh_token)
    token_row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_row.expires_at < datetime.now(UTC):
        db.delete(token_row)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.id == token_row.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db.delete(token_row)
    db.commit()

    new_access = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh = _issue_refresh_token(str(user.id), db)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _to_user_out(current_user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: MeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.city_zone is not None:
        current_user.city_zone = payload.city_zone
    if payload.worker_category is not None:
        current_user.worker_category = payload.worker_category

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return _to_user_out(current_user)
