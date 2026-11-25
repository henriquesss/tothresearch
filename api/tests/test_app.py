import logging

import pytest
from fastapi import FastAPI

from app.main import create_app


def test_create_app_returns_fastapi_app() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)


def test_log_level_setting_sets_the_app_logger_level(monkeypatch: pytest.MonkeyPatch) -> None:
    app_logger = logging.getLogger("app")
    previous = app_logger.level
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    try:
        create_app()

        assert app_logger.level == logging.DEBUG
        assert logging.getLogger("app.api.health").isEnabledFor(logging.DEBUG)
    finally:
        app_logger.setLevel(previous)
