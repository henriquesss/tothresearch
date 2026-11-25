import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.db import create_engine

ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")


def check_test_database_url(database_url: str | None, test_database_url: str | None) -> str:
    """Return TEST_DATABASE_URL, or raise when it is unset or equal to DATABASE_URL."""
    if not test_database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL is unset; the API tests need a database separate from DATABASE_URL."
        )
    if test_database_url == database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL equals DATABASE_URL; the API tests refuse to run against "
            "the application database."
        )
    return test_database_url


def pytest_sessionstart(session: pytest.Session) -> None:
    try:
        check_test_database_url(
            os.environ.get("DATABASE_URL"), os.environ.get("TEST_DATABASE_URL")
        )
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=4)


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return check_test_database_url(
        os.environ.get("DATABASE_URL"), os.environ.get("TEST_DATABASE_URL")
    )


@pytest.fixture(scope="session")
async def test_engine(test_database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_engine(test_database_url)
    yield engine
    await engine.dispose()
