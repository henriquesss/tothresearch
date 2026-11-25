from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    openrouter_api_key: SecretStr | None = None
    admin_api_key: SecretStr | None = None
    session_secret: SecretStr | None = None
    log_level: str = "INFO"


def load_settings() -> Settings:
    """Read settings from the environment; exit naming any missing required variable."""
    try:
        return Settings()
    except ValidationError as exc:
        missing = sorted(
            str(error["loc"][0]).upper() for error in exc.errors() if error["type"] == "missing"
        )
        if missing:
            raise SystemExit(
                f"Missing required environment variable(s): {', '.join(missing)}"
            ) from None
        raise
