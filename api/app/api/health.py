import asyncio
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

router = APIRouter()

DATABASE_TIMEOUT_SECONDS = 2.0


async def _database_answers(engine: AsyncEngine) -> bool:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True


@router.get("/api/health")
async def health(request: Request) -> JSONResponse:
    engine: AsyncEngine = request.app.state.engine
    try:
        await asyncio.wait_for(_database_answers(engine), timeout=DATABASE_TIMEOUT_SECONDS)
    except Exception:
        logger.warning("Health check: database did not answer SELECT 1", exc_info=True)
        return JSONResponse(
            status_code=503, content={"status": "degraded", "database": "unavailable"}
        )
    return JSONResponse(status_code=200, content={"status": "ok", "database": "ok"})
