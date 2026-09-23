"""Generation pipeline (PRD §10).

Flow: entitlement → ownership → duplicate guard → job → AI → validate →
DOCX → PDF → upload both → persist → ready.

Atomic: any failure leaves NO partial document — the RAMS is marked failed
with a safe error message, and orphan uploads are cleaned up best-effort.
"""

from typing import Any

from app.core.errors import ApiError
from app.integrations.ai import AiError, get_ai_provider
from app.integrations.storage import (
    RAMS_DOCUMENTS_BUCKET,
    StorageClient,
    StorageError,
    rams_doc_path,
)
from app.repositories.generation_jobs import GenerationJobsRepo, now_iso
from app.repositories.profiles import ProfilesRepo
from app.repositories.rams import RamsRepo
from app.services.document import build_rams_docx
from app.services.entitlement import check_entitlement
from app.services.pdf import build_rams_pdf

# Document production completes a content-ready RAMS into "ready".
READY = "ready"
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

    # 5. AI → validate → documents → upload → persist
    uploaded: list[str] = []
    try:
        provider = get_ai_provider()
        output = provider.generate(rams.get("input_data") or {})
        generated = output.model_dump(mode="json")

        profile = ProfilesRepo().get(user_id)
        doc_number = rams.get("document_number") or rams_id
        docx_bytes = build_rams_docx(rams.get("input_data") or {}, generated, profile, doc_number)
        pdf_bytes = build_rams_pdf(rams.get("input_data") or {}, generated, profile, doc_number)

        storage = StorageClient.from_settings()
        docx_path = rams_doc_path(user_id, rams_id, "docx")
        pdf_path = rams_doc_path(user_id, rams_id, "pdf")
        storage.upload(
            RAMS_DOCUMENTS_BUCKET,
            docx_path,
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        uploaded.append(docx_path)
        storage.upload(RAMS_DOCUMENTS_BUCKET, pdf_path, pdf_bytes, "application/pdf")
        uploaded.append(pdf_path)

        rams_repo.update(
            user_id,
            rams_id,
            {
                "status": READY,
                "generated_data": generated,
                "docx_path": docx_path,
                "pdf_path": pdf_path,
                "generation_error": None,
            },
        )
        jobs_repo.mark(job["id"], {"status": "succeeded", "completed_at": now_iso()})
        updated = rams_repo.get(user_id, rams_id)
        return {"status": READY, "rams": updated, "provider": provider.name}
    except AiError as exc:
        code = exc.code
        _fail(rams_repo, jobs_repo, user_id, rams_id, job["id"], code, uploaded)
        raise ApiError(502, code, _safe_message()) from exc
    except (ValueError, StorageError) as exc:
        code = "DOCX_GENERATION_FAILED" if isinstance(exc, ValueError) else "STORAGE_UPLOAD_FAILED"
        _fail(rams_repo, jobs_repo, user_id, rams_id, job["id"], code, uploaded)
        raise ApiError(502, code, _safe_message()) from exc


def _safe_message() -> str:
    return (
        "We couldn't generate your RAMS right now. "
        "No document has been created. Please try again."
    )


def _fail(
    rams_repo: RamsRepo,
    jobs_repo: GenerationJobsRepo,
    user_id: str,
    rams_id: str,
    job_id: str,
    code: str,
    uploaded: list[str],
) -> None:
    message = _safe_message()
    # Best-effort orphan cleanup: never expose a partial file set
    if uploaded:
        StorageClient.from_settings().remove(RAMS_DOCUMENTS_BUCKET, uploaded)
    rams_repo.update(user_id, rams_id, {"status": FAILED, "generation_error": message})
    jobs_repo.mark(
        job_id,
        {
            "status": "failed",
            "completed_at": now_iso(),
            "error_code": code,
            "error_message": message,
        },
    )
