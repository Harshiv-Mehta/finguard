from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from db_models import Transaction
from schemas import AnalysisResponse, DashboardResponse, TransactionInput, TransactionResponse
from services import analyze_transaction, build_dashboard, save_transaction


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="FinGuard", version="1.0.0")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(payload: TransactionInput, db: Session = Depends(get_db)):
    try:
        return analyze_transaction(db, payload)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/transactions", response_model=TransactionResponse)
def create_transaction(payload: TransactionInput, db: Session = Depends(get_db)):
    analysis = analyze_transaction(db, payload)
    return save_transaction(db, payload, analysis)


@app.get("/api/transactions", response_model=list[TransactionResponse])
def list_transactions(db: Session = Depends(get_db)):
    return build_dashboard(db)["recent_transactions"]


@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return build_dashboard(db)


@app.delete("/api/transactions")
def clear_transactions(db: Session = Depends(get_db)):
    db.query(Transaction).delete()
    db.commit()
    return {"status": "ok"}
