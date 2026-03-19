from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import SESSION_COOKIE_NAME, SESSION_DURATION
from app.core.settings import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, UserCredentials
from app.schemas.transaction import AnalysisResponse, DashboardResponse, TransactionInput, TransactionResponse
from app.services.analysis_service import analyze_transaction
from app.services.auth_service import (
    authenticate_user,
    create_user,
    create_user_session,
    get_user_by_session_token,
    invalidate_session,
)
from app.services.dashboard_service import build_dashboard
from app.services.transaction_service import clear_transactions, list_transactions, save_transaction


site_router = APIRouter()
api_router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(Path(settings.templates_dir)))


@site_router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = get_user_by_session_token(db, request.cookies.get(SESSION_COOKIE_NAME))
    template_name = "index.html" if user else "login.html"
    return templates.TemplateResponse(template_name, {"request": request, "user": user})

@api_router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCredentials, request: Request, response: Response, db: Session = Depends(get_db)):
    user = create_user(db, email=payload.email, password=payload.password)
    token = create_user_session(db, user=user)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
        max_age=int(SESSION_DURATION.total_seconds()),
    )
    return {"email": user.email}


@api_router.post("/auth/login", response_model=AuthResponse)
def login(payload: UserCredentials, request: Request, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=payload.email, password=payload.password)
    token = create_user_session(db, user=user)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
        max_age=int(SESSION_DURATION.total_seconds()),
    )
    return {"email": user.email}


@api_router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    invalidate_session(db, request.cookies.get(SESSION_COOKIE_NAME))
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@api_router.post("/analyze", response_model=AnalysisResponse)
def analyze(
    payload: TransactionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analyze_transaction(db, current_user, payload)


@api_router.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    payload: TransactionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = analyze_transaction(db, current_user, payload)
    return save_transaction(db, current_user, payload, analysis)


@api_router.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_transactions(db, current_user, limit=limit, offset=offset, category=category)


@api_router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return build_dashboard(db, current_user)


@api_router.delete("/transactions")
def delete_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    clear_transactions(db, current_user)
    return {"status": "ok"}
