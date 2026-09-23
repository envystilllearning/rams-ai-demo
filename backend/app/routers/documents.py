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
from app.repositories.profiles import ProfilesRepo
from app.repositories.rams import RamsRepo
from app.services.document import build_rams_docx

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
