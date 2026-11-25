import logging

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

GENERIC_500 = {"error": "internal_error", "message": "An unexpected error occurred."}
NOT_FOUND_404 = {"error": "not_found", "message": "Resource not found."}


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    async def boom() -> None:
        raise RuntimeError("secret /path detail")

    app.add_api_route("/api/test-only/raise", boom)
    return TestClient(app, raise_server_exceptions=False)


def test_unhandled_exception_returns_generic_500(client: TestClient) -> None:
    response = client.get("/api/test-only/raise")

    assert response.status_code == 500
    assert response.json() == GENERIC_500
    for leaked in ("RuntimeError", "secret", "/path", "Traceback"):
        assert leaked not in response.text


def test_unhandled_exception_logs_traceback(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR):
        client.get("/api/test-only/raise")

    error_texts = [
        caplog.handler.format(record)
        for record in caplog.records
        if record.levelno == logging.ERROR
    ]
    assert any("Traceback" in text for text in error_texts)


def test_unknown_api_path_returns_404_envelope(client: TestClient) -> None:
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_404


def test_api_prefix_match_is_exact(client: TestClient) -> None:
    assert client.get("/api").json() == NOT_FOUND_404

    response = client.get("/apix")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
