# FinGuard - AI Financial Safety Net

FinGuard is a full-stack Python website with a professional frontend, a FastAPI backend, and a SQLite or Postgres database. The Python project has been reorganized into a stronger production-style structure with configuration management, service modules, tests, and Alembic migrations.

## Stack

- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: FastAPI
- Database: SQLite with SQLAlchemy
- Analytics: Pandas
- Optional ML: scikit-learn logistic regression
- Tooling: Pytest, Alembic, Pydantic Settings

## Features

- Professional browser-based dashboard
- Analyze-first transaction workflow
- Risk scoring and smart financial alerts
- Impulse-spend detection from recent activity
- Category and balance charts fed from API data
- Persistent SQLite database storage
- One-click history reset
- Typed enums for API inputs and outputs
- Paginated transaction endpoint support
- Test suite for risk logic, simulation, and API behavior
- Alembic migration scaffolding

## Project Structure

```text
finguard/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── alembic/
├── tests/
├── pyproject.toml
├── main.py
├── database.py
├── db_models.py
├── schemas.py
├── services.py
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

## Run Tests

```bash
pytest
```

## Run Migrations

```bash
alembic upgrade head
```

## Notes

- This project uses simulated inputs only.
- No real banking or payment APIs are used.
- Data is stored locally in `finguard.db`.
