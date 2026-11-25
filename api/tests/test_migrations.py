import os
import subprocess
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]


def _alembic(*args: str, database_url: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DATABASE_URL": database_url}
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_upgrade_head_then_downgrade_base(test_database_url: str) -> None:
    upgrade = _alembic("upgrade", "head", database_url=test_database_url)
    assert upgrade.returncode == 0, upgrade.stderr

    current = _alembic("current", database_url=test_database_url)
    assert current.returncode == 0, current.stderr
    assert "0001_baseline" in current.stdout

    downgrade = _alembic("downgrade", "base", database_url=test_database_url)
    assert downgrade.returncode == 0, downgrade.stderr

    after = _alembic("current", database_url=test_database_url)
    assert after.returncode == 0, after.stderr
    assert "0001_baseline" not in after.stdout
