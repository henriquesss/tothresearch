import os
import re
import subprocess
import sys
from pathlib import Path

from app.core.config import Settings

API_DIR = Path(__file__).resolve().parents[1]
ENV_EXAMPLE = API_DIR.parent / ".env.example"


def test_missing_database_url_exits_naming_it() -> None:
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}

    result = subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "0"],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode != 0
    assert "DATABASE_URL" in result.stderr


def test_empty_database_url_exits_naming_it() -> None:
    env = {**os.environ, "DATABASE_URL": ""}

    result = subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "0"],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode != 0
    assert "DATABASE_URL" in result.stderr


def test_env_example_matches_settings() -> None:
    lines = ENV_EXAMPLE.read_text().splitlines()
    variables: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line)
        if match:
            variables[match.group(1)] = index

    declared = {name.upper() for name in Settings.model_fields}
    assert set(variables) == declared

    for name, index in variables.items():
        assert lines[index].split("=", 1)[1] != "", f"{name} has no placeholder value"
        assert index > 0 and lines[index - 1].startswith("# "), f"{name} has no comment line"
