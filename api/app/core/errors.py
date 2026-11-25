import logging
import re
from http import HTTPStatus
from typing import Any, cast, get_args

from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic_core.core_schema import ErrorType
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

# pydantic's own messages are templates that never quote the input; custom validators'
# messages (value_error, assertion_error, PydanticCustomError types) may, so they are replaced.
_TEMPLATED_ERROR_TYPES = set(get_args(ErrorType)) - {"value_error", "assertion_error"}
_DECLARED_NAME = re.compile(r"^[a-z_][a-z0-9_]*$")


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
        try:
            phrase = HTTPStatus(exc.status_code).phrase
        except ValueError:
            phrase = "Error"
        content = {
            "error": re.sub(r"[^a-z0-9]+", "_", phrase.lower()).strip("_"),
            "message": exc.detail if isinstance(exc.detail, str) else phrase,
        }
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


async def _validation_error(request: Request, exc: Exception) -> Response:
    exc = cast(RequestValidationError, exc)
    if not _is_api_path(request):
        return await request_validation_exception_handler(request, exc)
    # Never the submitted `input`/`ctx`, custom validator text, or submitted key names.
    fields = [{"field": _field(error), "issue": _issue(error)} for error in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed.",
            "fields": fields,
        },
    )


def _field(error: dict[str, Any]) -> str:
    loc = list(error["loc"])
    if error["type"] == "extra_forbidden" and len(loc) > 1:
        loc[-1] = "*"
    parts = [
        str(part) if isinstance(part, int) or _DECLARED_NAME.match(str(part)) else "*"
        for part in loc
    ]
    return ".".join(parts)


def _issue(error: dict[str, Any]) -> str:
    return str(error["msg"]) if error["type"] in _TEMPLATED_ERROR_TYPES else "Invalid value."


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _unhandled_exception)
    app.add_exception_handler(StarletteHTTPException, _http_exception)
    app.add_exception_handler(RequestValidationError, _validation_error)
