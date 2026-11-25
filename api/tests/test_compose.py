import re
from pathlib import Path
from typing import Any

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT_DIR / "docker-compose.yml"
API_DOCKERFILE = ROOT_DIR / "api" / "Dockerfile"


def load_services() -> dict[str, Any]:
    compose = yaml.safe_load(COMPOSE_FILE.read_text())
    services: dict[str, Any] = compose["services"]
    return services


def test_api_waits_for_healthy_db() -> None:
    services = load_services()

    assert services["api"]["depends_on"]["db"]["condition"] == "service_healthy"
    assert services["db"]["healthcheck"]["test"]


def test_api_entrypoint_migrates_before_uvicorn() -> None:
    api = load_services()["api"]
    # The image's own start command must not be replaced by compose.
    assert "command" not in api
    assert "entrypoint" not in api

    start = [
        line
        for line in API_DOCKERFILE.read_text().splitlines()
        if re.match(r"^\s*(CMD|ENTRYPOINT)\b", line)
    ]
    assert len(start) == 1
    command = start[0]
    assert "alembic upgrade head" in command
    assert "uvicorn" in command
    assert command.index("alembic upgrade head") < command.index("uvicorn")
    assert "&&" in command[command.index("alembic upgrade head") : command.index("uvicorn")]


def test_default_host_ports_match_the_spec() -> None:
    services = load_services()

    assert "${API_PORT:-8000}:8000" in services["api"]["ports"]
    assert "${WEB_PORT:-5173}:5173" in services["web"]["ports"]


def test_web_waits_for_healthy_api() -> None:
    services = load_services()

    check = " ".join(services["api"]["healthcheck"]["test"])
    assert "urllib" in check
    assert "/api/health" in check
    assert services["web"]["depends_on"]["api"]["condition"] == "service_healthy"
