"""RAMS CRUD endpoints (PRD §8, §24).

POST   /api/rams        — create draft from validated form input
GET    /api/rams        — list own RAMS (newest first)
GET    /api/rams/{id}   — detail (ownership checked)
DELETE /api/rams/{id}   — delete (ownership checked)

Generation lives in the AI phase: POST /api/rams/{id}/generate.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query

from app.core.deps import UserAuth
from app.integrations.storage import RAMS_DOCUMENTS_BUCKET, StorageClient
from app.repositories.rams import RamsRepo
from app.schemas.rams import RamsCreate, RamsListOut, RamsOut

router = APIRouter(prefix="/api/rams", tags=["rams"])

MAX_LIST_LIMIT = 100


def _new_document_number() -> str:
    """Human-friendly unique document number, e.g. RAMS-0004F2A1."""
    return f"RAMS-{uuid.uuid4().hex[:8].upper()}"


@router.post("", response_model=RamsOut, status_code=201)
async def create_rams(payload: RamsCreate, user: UserAuth) -> RamsOut:
    repo = RamsRepo()
    row = repo.create(
        user.id,
        {
            "document_number": _new_document_number(),
            "project_name": payload.project_name.strip(),
            "site_address": payload.site_address,
            "client_name": payload.client_name,
            "project_reference": payload.project_reference,
            "input_data": payload.model_dump(mode="json"),
        },
    )
    return RamsOut.model_validate(row)


@router.get("", response_model=RamsListOut)
async def list_rams(
    user: UserAuth,
    limit: int = Query(default=20, ge=1, le=MAX_LIST_LIMIT),
    offset: int = Query(default=0, ge=0),
) -> RamsListOut:
    repo = RamsRepo()
    items, total = repo.list_for_user(user.id, limit=limit, offset=offset)
    return RamsListOut(
        items=[RamsOut.model_validate(i) for i in items],
        total=total,
    )


@router.get("/{rams_id}", response_model=RamsOut)
async def get_rams(rams_id: str, user: UserAuth) -> RamsOut:
    repo = RamsRepo()
    row = repo.get(user.id, rams_id)
    if row is None:
        raise HTTPException(status_code=404, detail="RAMS not found")
    return RamsOut.model_validate(row)


@router.delete("/{rams_id}", status_code=204)
async def delete_rams(rams_id: str, user: UserAuth) -> None:
    repo = RamsRepo()
    existing = repo.get(user.id, rams_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="RAMS not found")
    deleted = repo.delete(user.id, rams_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="RAMS not found")
    # Best-effort: remove persistent files so no orphans remain
    paths = [p for p in (existing.get("docx_path"), existing.get("pdf_path")) if p]
    if paths:
        StorageClient.from_settings().remove(RAMS_DOCUMENTS_BUCKET, paths)
