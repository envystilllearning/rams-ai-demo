"""Profile repository — Supabase REST via service role (server-side only)."""

from typing import Any

import httpx

from app.core.config import get_settings


class ProfilesRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.base = f"{s.supabase_url}/rest/v1"
        self.headers = {
            "apikey": s.supabase_service_role_key,
            "Authorization": f"Bearer {s.supabase_service_role_key}",
            "Content-Type": "application/json",
        }

    def get(self, user_id: str) -> dict[str, Any] | None:
        with httpx.Client(timeout=15) as c:
            r = c.get(
                f"{self.base}/profiles",
                params={"select": "*", "id": f"eq.{user_id}"},
                headers=self.headers,
            )
            r.raise_for_status()
            rows = r.json()
            return rows[0] if rows else None

    def upsert(self, user_id: str, email: str | None, data: dict[str, Any]) -> dict[str, Any]:
        row = {"id": user_id, **({"email": email} if email else {}), **data}
        with httpx.Client(timeout=15) as c:
            r = c.post(
                f"{self.base}/profiles",
                params={"on_conflict": "id"},
                headers={**self.headers, "Prefer": "return=representation"},
                json=row,
            )
            r.raise_for_status()
            return r.json()[0]

    def update(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=15) as c:
            r = c.patch(
                f"{self.base}/profiles",
                params={"id": f"eq.{user_id}"},
                headers={**self.headers, "Prefer": "return=representation"},
                json=data,
            )
            r.raise_for_status()
            rows = r.json()
            if not rows:
                raise ValueError("Profile not found")
            return rows[0]
