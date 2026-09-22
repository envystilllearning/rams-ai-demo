"""Profile endpoints: GET/PATCH /api/profile (PRD §7, §24)."""

from fastapi import APIRouter, HTTPException

from app.core.deps import UserAuth
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
