import logging

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError, field_validator

from app.main import create_app

GENERIC_500 = {"error": "internal_error", "message": "An unexpected error occurred."}
NOT_FOUND_404 = {"error": "not_found", "message": "Resource not found."}


class Signup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str

    @field_validator("email")
    @classmethod
    def quote_input(cls, v: str) -> str:
        raise ValueError(f"invalid email {v}")


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    async def boom() -> None:
        raise RuntimeError("secret /path detail")

    async def needs_int(n: int) -> int:
        return n

    async def conflict() -> None:
        raise HTTPException(409, "Already exists")

    async def conflict_dict() -> None:
        raise HTTPException(409, {"reason": "duplicate"})

    async def signup(body: Signup) -> None:
        return None

    async def scores(body: dict[str, int]) -> None:
        return None

    async def teapot() -> None:
        raise HTTPException(418, "short and stout")

    async def nonstandard() -> None:
        raise HTTPException(499, "client closed")

    app.add_api_route("/api/test-only/signup", signup, methods=["POST"])
    app.add_api_route("/api/test-only/scores", scores, methods=["POST"])
    app.add_api_route("/api/test-only/teapot", teapot)
    app.add_api_route("/api/test-only/nonstandard", nonstandard)
    app.add_api_route("/api/test-only/raise", boom)
    app.add_api_route("/api/test-only/int", needs_int)
    app.add_api_route("/api/test-only/conflict", conflict)
    app.add_api_route("/api/test-only/conflict-dict", conflict_dict)
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


def test_method_not_allowed_returns_405_envelope(client: TestClient) -> None:
    response = client.post("/api/health")

    assert response.status_code == 405
    assert response.json() == {"error": "method_not_allowed", "message": "Method not allowed."}


def test_validation_error_returns_422_without_input(client: TestClient) -> None:
    with pytest.raises(ValidationError) as excinfo:
        TypeAdapter(int).validate_python("secretvalue")
    pydantic_msg = excinfo.value.errors()[0]["msg"]

    response = client.get("/api/test-only/int?n=secretvalue")

    assert response.status_code == 422
    assert response.json() == {
        "error": "validation_error",
        "message": "Request validation failed.",
        "fields": [{"field": "query.n", "issue": pydantic_msg}],
    }
    assert "secretvalue" not in response.text


def test_http_exception_returns_envelope_with_detail(client: TestClient) -> None:
    response = client.get("/api/test-only/conflict")

    assert response.status_code == 409
    assert response.json() == {"error": "conflict", "message": "Already exists"}

    response = client.get("/api/test-only/conflict-dict")

    assert response.status_code == 409
    assert response.json() == {"error": "conflict", "message": "Conflict"}


def test_validation_error_never_echoes_custom_validator_text(client: TestClient) -> None:
    response = client.post("/api/test-only/signup", json={"email": "hunter2secret"})

    assert response.status_code == 422
    assert response.json() == {
        "error": "validation_error",
        "message": "Request validation failed.",
        "fields": [{"field": "body.email", "issue": "Invalid value."}],
    }
    assert "hunter2secret" not in response.text


def test_validation_error_never_echoes_submitted_keys(client: TestClient) -> None:
    extra = client.post(
        "/api/test-only/signup", json={"email": "a@b.co", "s3cr3t-token-key": "x"}
    )
    keyed = client.post("/api/test-only/scores", json={"s3cr3t-token-key": "x"})

    for response in (extra, keyed):
        assert response.status_code == 422
        assert "s3cr3t-token-key" not in response.text
    assert {"field": "body.*", "issue": "Extra inputs are not permitted"} in extra.json()[
        "fields"
    ]
    assert keyed.json()["fields"][0]["field"] == "body.*"


def test_http_exception_error_code_is_snake_case(client: TestClient) -> None:
    response = client.get("/api/test-only/teapot")

    assert response.status_code == 418
    assert response.json() == {"error": "i_m_a_teapot", "message": "short and stout"}


def test_http_exception_with_unknown_status_keeps_its_status(client: TestClient) -> None:
    response = client.get("/api/test-only/nonstandard")

    assert response.status_code == 499
    assert response.json() == {"error": "error", "message": "client closed"}
