"""Generation pipeline (PRD §10).

Flow: entitlement → ownership → duplicate guard → job → AI → validate →
persist generated content. Atomic: any failure leaves NO partial document —
the RAMS is marked failed with a safe error message.
"""

from typing import Any

from app.core.errors import ApiError
from app.integrations.ai import AiError, get_ai_provider
from app.repositories.generation_jobs import GenerationJobsRepo, now_iso
from app.repositories.rams import RamsRepo
from app.services.entitlement import check_entitlement

# Document production (F10/F11) completes a "generated" RAMS into "ready".
CONTENT_READY = "generated"
FAILED = "failed"


def run_generation(user_id: str, rams_id: str) -> dict[str, Any]:
    rams_repo = RamsRepo()
    jobs_repo = GenerationJobsRepo()

    # 1. Ownership
    rams = rams_repo.get(user_id, rams_id)
    if rams is None:
        raise ApiError(404, "DOCUMENT_NOT_FOUND", "RAMS not found")

    # 2. Entitlement — backend is the authority (§17)
    if not check_entitlement(user_id):
        raise ApiError(
            403,
            "SUBSCRIPTION_REQUIRED",
            "An active subscription is required to generate a RAMS.",
        )

    # 3. Duplicate guard (§44)
    if jobs_repo.active_for_rams(user_id, rams_id):
        raise ApiError(
            409,
            "GENERATION_IN_PROGRESS",
            "A generation is already running for this RAMS.",
        )

    # 4. Create job + mark RAMS generating
    try:
        job = jobs_repo.create(user_id, rams_id)
    except ValueError as exc:
        raise ApiError(
            409,
            "GENERATION_IN_PROGRESS",
            "A generation is already running for this RAMS.",
        ) from exc
    rams_repo.update(user_id, rams_id, {"status": "generating", "generation_error": None})
    jobs_repo.mark(job["id"], {"status": "running", "started_at": now_iso(), "attempts": 1})

    # 5. AI → validate → persist
    try:
        provider = get_ai_provider()
        output = provider.generate(rams.get("input_data") or {})
        rams_repo.update(
            user_id,
            rams_id,
            {
                "status": CONTENT_READY,
                "generated_data": output.model_dump(mode="json"),
                "generation_error": None,
            },
        )
        jobs_repo.mark(
            job["id"], {"status": "succeeded", "completed_at": now_iso()}
        )
        updated = rams_repo.get(user_id, rams_id)
        return {"status": CONTENT_READY, "rams": updated, "provider": provider.name}
    except AiError as exc:
        safe_message = (
            "We couldn't generate your RAMS right now. "
            "No document has been created. Please try again."
        )
        rams_repo.update(
            user_id, rams_id, {"status": FAILED, "generation_error": safe_message}
        )
        jobs_repo.mark(
            job["id"],
            {
                "status": "failed",
                "completed_at": now_iso(),
                "error_code": exc.code,
                "error_message": safe_message,
            },
        )
        raise ApiError(502, exc.code, safe_message) from exc
