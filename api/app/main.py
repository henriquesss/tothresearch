from fastapi import FastAPI

from app.core.config import load_settings
from app.core.db import create_engine, create_session_factory
from app.core.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Toth Research API")
    settings = load_settings()
    app.state.settings = settings
    app.state.engine = create_engine(settings.database_url)
    app.state.session_factory = create_session_factory(app.state.engine)
    register_error_handlers(app)
    return app


app = create_app()
