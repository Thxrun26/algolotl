"""Config-driven settings via Pydantic. Everything overridable by env vars."""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ALGO_", env_file=".env", extra="ignore")

    app_name: str = "Algolotl"
    environment: str = "development"
    # Secret used to sign JWTs. MUST be overridden in production via ALGO_SECRET_KEY.
    secret_key: str = Field(default="dev-only-change-me-in-prod")
    access_token_ttl_min: int = 60 * 24 * 7  # 7 days
    # Comma-separated allowed origins for CORS; "*" for dev only.
    cors_origins: str = "*"
    # Where the JSON data store lives (users + progress). Zero-DB by default.
    data_dir: str = "./_store"
    # Optional OpenAI-compatible endpoint for the AI assistant (falls back to
    # a built-in offline tutor if unset — no key required to run).
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    # Google OAuth (optional; documented in README). Empty => disabled.
    google_client_id: str = ""
    google_client_secret: str = ""

    @property
    def is_prod(self) -> bool:
        return self.environment.lower() in ("production", "prod")

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
