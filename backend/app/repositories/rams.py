"""RAMS repository — ownership enforced at every query (PRD §26/§27)."""

from typing import Any

import httpx

from app.core.config import get_settings


class RamsRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.base = f"{s.supabase_url}/rest/v1"
        self.headers = {
            "apikey": s.supabase_service_role_key,
            "Authorization": f"Bearer {s.supabase_service_role_key}",
            "Content-Type": "application/json",
        }

    def list_for_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[dict], int]:
        """Return (items, total) for the user, newest first."""
        with httpx.Client(timeout=15) as c:
            r = c.get(
                f"{self.base}/rams",
                params={
                    "select": "*",
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc",
                    "limit": str(limit),
                    "offset": str(offset),
                },
                headers={**self.headers, "Prefer": "count=exact"},
            )
            r.raise_for_status()
            items = r.json()
            total = int(r.headers.get("Content-Range", "0").split("/")[-1] or 0)
            return items, total

    def get(self, user_id: str, rams_id: str) -> dict | None:
        """Fetch a single RAMS — always scoped to owner (Risk 5, PRD §55)."""
        with httpx.Client(timeout=15) as c:
            r = c.get(
                f"{self.base}/rams",
                params={"select": "*", "id": f"eq.{rams_id}", "user_id": f"eq.{user_id}"},
                headers=self.headers,
            )
            r.raise_for_status()
            rows = r.json()
            return rows[0] if rows else None

    def create(self, user_id: str, data: dict[str, Any]) -> dict:
        row = {"user_id": user_id, "status": "draft", **data}
        with httpx.Client(timeout=15) as c:
            r = c.post(
                f"{self.base}/rams",
                headers={**self.headers, "Prefer": "return=representation"},
                json=row,
            )
            r.raise_for_status()
            return r.json()[0]

    def update(self, user_id: str, rams_id: str, data: dict[str, Any]) -> dict | None:
        with httpx.Client(timeout=15) as c:
            r = c.patch(
                f"{self.base}/rams",
                params={"id": f"eq.{rams_id}", "user_id": f"eq.{user_id}"},
                headers={**self.headers, "Prefer": "return=representation"},
                json=data,
            )
            r.raise_for_status()
            rows = r.json()
            return rows[0] if rows else None

    def delete(self, user_id: str, rams_id: str) -> bool:
        with httpx.Client(timeout=15) as c:
            r = c.delete(
                f"{self.base}/rams",
                params={"id": f"eq.{rams_id}", "user_id": f"eq.{user_id}"},
                headers=self.headers,
            )
            r.raise_for_status()
            return r.status_code in (200, 204)

    def count_by_status(self, user_id: str, statuses: tuple[str, ...]) -> int:
        """Count active jobs — used for duplicate generation protection (§44)."""
        status_filter = ",".join(statuses)
        with httpx.Client(timeout=15) as c:
            r = c.get(
                f"{self.base}/generation_jobs",
                params={
                    "select": "id",
                    "user_id": f"eq.{user_id}",
                    "status": f"in.({status_filter})",
                },
                headers={**self.headers, "Prefer": "count=exact"},
            )
            r.raise_for_status()
            return int(r.headers.get("Content-Range", "0").split("/")[-1] or 0)
