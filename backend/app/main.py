from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import ApiError, api_error_handler, unhandled_error_handler
from app.routers import billing, generation, health, profile, rams

settings = get_settings()

app = FastAPI(
    title="RAMS AI Demo API",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
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
app.include_router(generation.router)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)
