from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import require_user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    return require_user(request, db)
