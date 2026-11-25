import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import load_settings
from app.core.db import create_engine, create_session_factory
from app.core.errors import register_error_handlers


def configure_logging(level: str) -> None:
    """Send the API's own log records to stderr at the configured LOG_LEVEL."""
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("app").setLevel(level.upper())


def create_app() -> FastAPI:
    app = FastAPI(title="Toth Research API")
    settings = load_settings()
    app.state.settings = settings
    configure_logging(settings.log_level)
    app.state.engine = create_engine(settings.database_url)
    app.state.session_factory = create_session_factory(app.state.engine)
    register_error_handlers(app)
    app.include_router(health_router)
    return app


app = create_app()
