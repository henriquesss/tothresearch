from fastapi import FastAPI

from app.core.config import load_settings
from app.core.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Toth Research API")
    app.state.settings = load_settings()
    register_error_handlers(app)
    return app


app = create_app()
