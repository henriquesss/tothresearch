from fastapi import FastAPI

from app.core.config import load_settings


def create_app() -> FastAPI:
    app = FastAPI(title="Toth Research API")
    app.state.settings = load_settings()
    return app


app = create_app()
