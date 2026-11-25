import logging
from http import HTTPStatus
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def _unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred."},
    )


def _is_api_path(request: Request) -> bool:
    path = request.url.path
    return path == "/api" or path.startswith("/api/")


async def _http_exception(request: Request, exc: Exception) -> Response:
    exc = cast(StarletteHTTPException, exc)
    if not _is_api_path(request):
        return await http_exception_handler(request, exc)
    if exc.status_code == 404:
        content = {"error": "not_found", "message": "Resource not found."}
    elif exc.status_code == 405:
        content = {"error": "method_not_allowed", "message": "Method not allowed."}
    else:
        phrase = HTTPStatus(exc.status_code).phrase
        content = {
            "error": phrase.lower().replace(" ", "_").replace("-", "_"),
            "message": exc.detail if isinstance(exc.detail, str) else phrase,
        }
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


async def _validation_error(request: Request, exc: Exception) -> Response:
    exc = cast(RequestValidationError, exc)
    if not _is_api_path(request):
        return await request_validation_exception_handler(request, exc)
    # Only the location and pydantic's message: never the submitted `input` or `ctx` values.
    fields = [
        {"field": ".".join(str(part) for part in error["loc"]), "issue": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed.",
            "fields": fields,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _unhandled_exception)
    app.add_exception_handler(StarletteHTTPException, _http_exception)
    app.add_exception_handler(RequestValidationError, _validation_error)
