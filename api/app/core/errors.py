import logging
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def _unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred."},
    )


async def _http_exception(request: Request, exc: Exception) -> Response:
    exc = cast(StarletteHTTPException, exc)
    if exc.status_code == 404 and request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": "Resource not found."},
        )
    return await http_exception_handler(request, exc)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _unhandled_exception)
    app.add_exception_handler(StarletteHTTPException, _http_exception)
