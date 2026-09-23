"""Vercel serverless entrypoint — re-exports the FastAPI ASGI app."""

from app.main import app  # noqa: F401  (Vercel looks for `app` in api/index.py)
