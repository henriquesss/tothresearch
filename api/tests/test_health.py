import socket
import time
from collections.abc import Iterator

import httpx
import pytest
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


@pytest.fixture
def silent_port() -> Iterator[int]:
    """A local TCP port that completes the handshake and then never replies."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(8)
        yield listener.getsockname()[1]


async def test_health_503_when_database_unreachable(silent_port: int) -> None:
    engine = create_engine(f"postgresql+asyncpg://toth:toth@127.0.0.1:{silent_port}/toth")
    try:
        started = time.monotonic()
        response = await _get_health(engine)
        elapsed = time.monotonic() - started
    finally:
        await engine.dispose()

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}
    assert 2 <= elapsed < 3
