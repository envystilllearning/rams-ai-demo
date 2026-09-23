"""Generation endpoint (PRD §10, §17, §24).

POST /api/rams/{id}/generate — auth → ownership → entitlement → run pipeline.
"""

from typing import Any

from fastapi import APIRouter

from app.core.deps import UserAuth
from app.core.errors import ApiError
from app.core.ratelimit import generate_limiter
from app.services.generation import run_generation

router = APIRouter(prefix="/api/rams", tags=["generation"])


@router.post("/{rams_id}/generate")
async def generate_rams(rams_id: str, user: UserAuth) -> dict[str, Any]:
    if not generate_limiter.allow(user.id):
        raise ApiError(
            429,
            "RATE_LIMITED",
            "Too many generation requests. Please wait a while and try again.",
        )
    result = run_generation(user.id, rams_id)
    rams = result["rams"] or {}
    return {
        "status": result["status"],
        "provider": result["provider"],
        "rams_id": rams_id,
        "generated_hazards": len((rams.get("generated_data") or {}).get("hazards", [])),
    }
