import os

import pytest
from conftest import check_test_database_url
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine


def test_guard_rejects_equal_urls() -> None:
    url = "postgresql+asyncpg://toth:toth@localhost:5432/toth"

    with pytest.raises(RuntimeError) as excinfo:
        check_test_database_url(url, url)

    assert "TEST_DATABASE_URL" in str(excinfo.value)
    assert "DATABASE_URL" in str(excinfo.value).replace("TEST_DATABASE_URL", "")


@pytest.mark.parametrize(
    ("database_url", "test_database_url"),
    [
        (
            "postgresql+asyncpg://toth:toth@127.0.0.1:5432/toth_test",
            "postgresql+asyncpg://toth:toth@localhost:5432/toth_test",
        ),
        (
            "postgresql+asyncpg://toth:toth@localhost/toth",
            "postgresql+asyncpg://other:pw@[::1]:5432/toth",
        ),
        (
            "postgresql+asyncpg://toth:toth@LOCALHOST:5432/toth",
            "postgresql://toth:toth@127.0.0.1/toth",
        ),
    ],
)
def test_guard_rejects_aliased_urls(database_url: str, test_database_url: str) -> None:
    with pytest.raises(RuntimeError) as excinfo:
        check_test_database_url(database_url, test_database_url)

    assert "TEST_DATABASE_URL" in str(excinfo.value)
    assert "DATABASE_URL" in str(excinfo.value).replace("TEST_DATABASE_URL", "")


def test_guard_accepts_a_different_database() -> None:
    test_url = "postgresql+asyncpg://toth:toth@localhost:5432/toth_test"

    assert (
        check_test_database_url("postgresql+asyncpg://toth:toth@127.0.0.1:5432/toth", test_url)
        == test_url
    )


async def test_fixture_engine_uses_test_database(test_engine: AsyncEngine) -> None:
    test_db_name = make_url(os.environ["TEST_DATABASE_URL"]).database
    app_db_name = make_url(os.environ["DATABASE_URL"]).database

    async with test_engine.connect() as connection:
        current = (await connection.execute(text("SELECT current_database()"))).scalar_one()

    assert current == test_db_name
    assert current != app_db_name
