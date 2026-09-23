"""On-demand DOCX download (PRD §15).

Builds deterministically from stored data — no temp files, no local paths
exposed. Persistent storage + signed URLs arrive in the storage phase.
"""

import io
import re

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.deps import UserAuth
from app.core.errors import ApiError
from app.integrations.storage import (
    RAMS_DOCUMENTS_BUCKET,
    StorageClient,
    StorageError,
)
from app.repositories.profiles import ProfilesRepo
from app.repositories.rams import RamsRepo
from app.services.document import build_rams_docx
from app.services.pdf import build_rams_pdf

router = APIRouter(prefix="/api/rams", tags=["documents"])


def _safe_filename(document_number: str | None, rams_id: str) -> str:
    base = document_number or rams_id[:8]
    base = re.sub(r"[^A-Za-z0-9_-]", "_", base)
    return f"{base}.docx"


@router.get("/{rams_id}/documents/docx")
async def download_docx(rams_id: str, user: UserAuth) -> StreamingResponse:
    repo = RamsRepo()
    rams = repo.get(user.id, rams_id)
    if rams is None:
        raise ApiError(404, "DOCUMENT_NOT_FOUND", "RAMS not found")

    generated = rams.get("generated_data")
    if not generated:
        raise ApiError(
            409,
            "DOCUMENT_NOT_READY",
            "Generate AI content before downloading the document.",
        )

    profile = ProfilesRepo().get(user.id)
    try:
        data = build_rams_docx(
            rams.get("input_data") or {},
            generated,
            profile,
            rams.get("document_number") or rams_id,
        )
    except ValueError as exc:
        raise ApiError(500, "DOCX_GENERATION_FAILED", str(exc)) from exc

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{_safe_filename(rams.get("document_number"), rams_id)}"'
        },
    )


def _safe_pdf_filename(document_number: str | None, rams_id: str) -> str:
    base = document_number or rams_id[:8]
    base = re.sub(r"[^A-Za-z0-9_-]", "_", base)
    return f"{base}.pdf"


@router.get("/{rams_id}/documents/pdf")
async def download_pdf(rams_id: str, user: UserAuth) -> StreamingResponse:
    repo = RamsRepo()
    rams = repo.get(user.id, rams_id)
    if rams is None:
        raise ApiError(404, "DOCUMENT_NOT_FOUND", "RAMS not found")

    generated = rams.get("generated_data")
    if not generated:
        raise ApiError(
            409,
            "DOCUMENT_NOT_READY",
            "Generate AI content before downloading the document.",
        )

    profile = ProfilesRepo().get(user.id)
    try:
        data = build_rams_pdf(
            rams.get("input_data") or {},
            generated,
            profile,
            rams.get("document_number") or rams_id,
        )
    except ValueError as exc:
        raise ApiError(500, "PDF_GENERATION_FAILED", str(exc)) from exc

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{_safe_pdf_filename(rams.get("document_number"), rams_id)}"'
        },
    )


@router.get("/{rams_id}/documents/{kind}/download")
async def download_stored(rams_id: str, kind: str, user: UserAuth) -> dict:
    """Signed-URL download for the persistent file (PRD §15).

    Verifies: auth → ownership → ready status → stored path exists.
    kind must be 'docx' or 'pdf'.
    """
    if kind not in ("docx", "pdf"):
        raise ApiError(400, "VALIDATION_ERROR", "kind must be 'docx' or 'pdf'")

    repo = RamsRepo()
    rams = repo.get(user.id, rams_id)
    if rams is None:
        raise ApiError(404, "DOCUMENT_NOT_FOUND", "RAMS not found")

    if rams.get("status") != "ready":
        raise ApiError(
            409,
            "DOCUMENT_NOT_READY",
            "The persistent document is not ready yet.",
        )

    path = rams.get("docx_path" if kind == "docx" else "pdf_path")
    if not path:
        raise ApiError(404, "DOCUMENT_NOT_FOUND", "Stored file not found")

    try:
        url = StorageClient.from_settings().create_signed_url(RAMS_DOCUMENTS_BUCKET, path)
    except StorageError as exc:
        raise ApiError(502, "STORAGE_DOWNLOAD_FAILED", "Could not prepare the download.") from exc

    filename = rams.get("document_number") or rams_id[:8]
    return {"url": url, "filename": f"{filename}.{kind}", "expires_in": 3600}
