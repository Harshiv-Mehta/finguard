# FinGuard - AI Financial Safety Net

FinGuard is now a full-stack Python website with a professional frontend, a FastAPI backend, and a SQLite database. It predicts risky spending behavior before a transaction is saved, explains the financial impact, and visualizes transaction history with a polished dashboard.

## Stack

- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: FastAPI
- Database: SQLite with SQLAlchemy
- Analytics: Pandas
- Optional ML: scikit-learn logistic regression

## Features

- Professional browser-based dashboard
- Analyze-first transaction workflow
- Risk scoring and smart financial alerts
- Impulse-spend detection from recent activity
- Category and balance charts fed from API data
- Persistent SQLite database storage
- One-click history reset

## Project Structure

```text
finguard/
├── main.py
├── database.py
├── db_models.py
├── schemas.py
├── services.py
├── risk_engine.py
├── simulation.py
├── model.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/styles.css
    └── js/app.js
```

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000`.

## Notes

- This project uses simulated inputs only.
- No real banking or payment APIs are used.
- Data is stored locally in `finguard.db`.
