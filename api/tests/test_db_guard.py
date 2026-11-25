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


async def test_fixture_engine_uses_test_database(test_engine: AsyncEngine) -> None:
    test_db_name = make_url(os.environ["TEST_DATABASE_URL"]).database
    app_db_name = make_url(os.environ["DATABASE_URL"]).database

    async with test_engine.connect() as connection:
        current = (await connection.execute(text("SELECT current_database()"))).scalar_one()

    assert current == test_db_name
    assert current != app_db_name
