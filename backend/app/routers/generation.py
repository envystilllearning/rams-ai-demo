"""Generation endpoint (PRD §10, §17, §24).

POST /api/rams/{id}/generate — auth → ownership → entitlement → run pipeline.
"""

from typing import Any

from fastapi import APIRouter

from app.core.deps import UserAuth
from app.services.generation import run_generation

router = APIRouter(prefix="/api/rams", tags=["generation"])


@router.post("/{rams_id}/generate")
async def generate_rams(rams_id: str, user: UserAuth) -> dict[str, Any]:
    result = run_generation(user.id, rams_id)
    rams = result["rams"] or {}
    return {
        "status": result["status"],
        "provider": result["provider"],
        "rams_id": rams_id,
        "generated_hazards": len((rams.get("generated_data") or {}).get("hazards", [])),
    }
