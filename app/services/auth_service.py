from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import (
    SESSION_COOKIE_NAME,
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expiry,
    verify_password,
)
from app.models.user import User
from app.models.user_session import UserSession


def create_user(db: Session, *, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email.")

    user = User(email=normalized_email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return user


def create_user_session(db: Session, *, user: User) -> str:
    token = generate_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=session_expiry(),
        )
    )
    db.commit()
    return token


def get_user_by_session_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None

    now = datetime.now(UTC)
    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == hash_session_token(token), UserSession.expires_at > now)
        .first()
    )
    if not session:
        return None
    return db.query(User).filter(User.id == session.user_id).first()


def invalidate_session(db: Session, token: str | None) -> None:
    if not token:
        return

    (
        db.query(UserSession)
        .filter(UserSession.token_hash == hash_session_token(token))
        .delete(synchronize_session=False)
    )
    db.commit()


def require_user(request: Request, db: Session) -> User:
    user = get_user_by_session_token(db, request.cookies.get(SESSION_COOKIE_NAME))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in to continue.")
    return user
