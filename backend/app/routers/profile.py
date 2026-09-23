"""Profile endpoints: GET/PATCH /api/profile (PRD §7, §24)."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.deps import UserAuth
from app.core.errors import ApiError
from app.integrations.storage import (
    COMPANY_ASSETS_BUCKET,
    LOGO_ALLOWED_MIME,
    LOGO_MAX_BYTES,
    StorageClient,
    StorageError,
)
from app.repositories.profiles import ProfilesRepo
from app.schemas.profile import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api", tags=["profile"])

EMPTY_PROFILE_FIELDS = {
    "full_name": None,
    "company_name": None,
    "company_address": None,
    "company_postcode": None,
    "company_phone": None,
    "logo_path": None,
}


@router.get("/profile", response_model=ProfileOut)
async def get_profile(user: UserAuth) -> ProfileOut:
    repo = ProfilesRepo()
    row = repo.get(user.id)
    if row is None:
        # First login: create an empty profile row for this user
        row = repo.upsert(user.id, user.email, EMPTY_PROFILE_FIELDS)
    return ProfileOut.model_validate(row)


@router.patch("/profile", response_model=ProfileOut)
async def update_profile(
    payload: ProfileUpdate,
    user: UserAuth,
) -> ProfileOut:
    repo = ProfilesRepo()
    data = payload.model_dump(exclude_unset=True)

    # Reject unknown/empty patch outright
    if not data:
        raise HTTPException(status_code=422, detail="No fields to update")

    try:
        row = repo.update(user.id, data)
    except ValueError:
        # Profile row missing (e.g. trigger did not run) — create then update
        repo.upsert(user.id, user.email, EMPTY_PROFILE_FIELDS)
        row = repo.update(user.id, data)
    return ProfileOut.model_validate(row)


@router.post("/profile/logo", response_model=ProfileOut)
async def upload_logo(
    user: UserAuth,
    file: UploadFile = File(...),  # noqa: B008 — standard FastAPI pattern
) -> ProfileOut:
    """Upload company logo → company-assets/{user_id}/logo.{ext}.

    Validates MIME + size; never trusts the uploaded filename (§27).
    """
    mime = (file.content_type or "").split(";")[0].strip().lower()
    ext = LOGO_ALLOWED_MIME.get(mime)
    if not ext:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            "Logo must be a PNG, JPEG or WebP image.",
        )

    data = await file.read()
    if len(data) == 0 or len(data) > LOGO_MAX_BYTES:
        raise ApiError(
            400,
            "VALIDATION_ERROR",
            "Logo must be non-empty and under 2 MB.",
        )

    path = f"{user.id}/logo.{ext}"
    try:
        StorageClient.from_settings().upload(COMPANY_ASSETS_BUCKET, path, data, mime)
    except StorageError as exc:
        raise ApiError(502, "STORAGE_UPLOAD_FAILED", "Logo upload failed.") from exc

    repo = ProfilesRepo()
    try:
        row = repo.update(user.id, {"logo_path": path})
    except ValueError:
        repo.upsert(user.id, user.email, EMPTY_PROFILE_FIELDS)
        row = repo.update(user.id, {"logo_path": path})
    return ProfileOut.model_validate(row)
