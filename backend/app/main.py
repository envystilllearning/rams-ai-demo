from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import ApiError, api_error_handler, unhandled_error_handler
from app.routers import billing, documents, generation, health, profile, rams

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Fail fast in production when required secrets are missing (PRD §27)."""
    import logging

    log = logging.getLogger("rams")
    required = {
        "SUPABASE_URL": settings.supabase_url,
        "SUPABASE_SERVICE_ROLE_KEY": settings.supabase_service_role_key,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        message = f"Missing required environment variables: {', '.join(missing)}"
        if settings.is_production:
            raise RuntimeError(message)
        log.warning("%s (development mode — continuing)", message)

    if settings.payment_provider == "stripe" and not settings.stripe_secret_key:
        message = "PAYMENT_PROVIDER=stripe but STRIPE_SECRET_KEY is empty"
        if settings.is_production:
            raise RuntimeError(message)
        log.warning("%s (development mode — continuing)", message)

    if settings.ai_provider == "openrouter" and not settings.openrouter_api_key:
        message = "AI_PROVIDER=openrouter but OPENROUTER_API_KEY is empty"
        if settings.is_production:
            raise RuntimeError(message)
        log.warning("%s (development mode — continuing)", message)

    yield


app = FastAPI(
    title="RAMS AI Demo API",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health.router)
app.include_router(profile.router)
app.include_router(billing.router)
app.include_router(rams.router)
app.include_router(documents.router)
app.include_router(generation.router)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)
