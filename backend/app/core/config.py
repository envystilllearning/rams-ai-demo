from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment (.env) per PRD §34."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"
    backend_cors_origins: str = "http://localhost:3000"

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""

    # AI (OpenRouter)
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"

    # Document worker (Gotenberg, PRD §13)
    gotenberg_url: str = "http://localhost:3100"

    # Subscription policy (PRD §4): past_due configurable, default No
    subscription_allow_past_due: bool = False

    # Payment provider: "mock" (demo, no Stripe keys needed) or "stripe"
    payment_provider: str = "mock"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
