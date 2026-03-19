from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.db.session import get_db
from app.schemas.transaction import AnalysisResponse, DashboardResponse, TransactionInput, TransactionResponse
from app.services.analysis_service import analyze_transaction
from app.services.dashboard_service import build_dashboard
from app.services.transaction_service import clear_transactions, list_transactions, save_transaction


site_router = APIRouter()
api_router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(Path(settings.templates_dir)))


@site_router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@api_router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: TransactionInput, db: Session = Depends(get_db)):
    return analyze_transaction(db, payload)


@api_router.post("/transactions", response_model=TransactionResponse)
def create_transaction(payload: TransactionInput, db: Session = Depends(get_db)):
    analysis = analyze_transaction(db, payload)
    return save_transaction(db, payload, analysis)


@api_router.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_transactions(db, limit=limit, offset=offset, category=category)


@api_router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return build_dashboard(db)


@api_router.delete("/transactions")
def delete_transactions(db: Session = Depends(get_db)):
    clear_transactions(db)
    return {"status": "ok"}
