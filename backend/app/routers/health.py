from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Basic health endpoint (PRD §24, §30)."""
    return {"status": "ok"}
