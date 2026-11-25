import time

import httpx
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.db import create_engine
from app.main import create_app


async def _get_health(engine: AsyncEngine) -> httpx.Response:
    app = create_app()
    app.state.engine = engine
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/api/health")


async def test_health_ok_when_database_answers(test_engine: AsyncEngine) -> None:
    response = await _get_health(test_engine)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_health_503_when_database_unreachable() -> None:
    engine = create_engine("postgresql+asyncpg://toth:toth@127.0.0.1:1/toth")
    try:
        started = time.monotonic()
        response = await _get_health(engine)
        elapsed = time.monotonic() - started
    finally:
        await engine.dispose()

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}
    assert elapsed < 3
