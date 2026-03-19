from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router, site_router
from app.core.exceptions import register_exception_handlers
from app.core.settings import get_settings
from app.db.bootstrap import bootstrap_database
from app.db.session import engine
from app.models.transaction import Transaction  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_session import UserSession  # noqa: F401


settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)
    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
    app.include_router(site_router)
    app.include_router(api_router, prefix=settings.api_prefix)
    register_exception_handlers(app)
    bootstrap_database(engine)
    return app


app = create_app()
