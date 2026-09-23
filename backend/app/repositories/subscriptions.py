"""Subscriptions repository — one row per user (upsert sync, PRD §16)."""

from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings


class SubscriptionsRepo:
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
                f"{self.base}/subscriptions",
                params={"select": "*", "user_id": f"eq.{user_id}"},
                headers=self.headers,
            )
            r.raise_for_status()
            rows = r.json()
            return rows[0] if rows else None

    def upsert(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        row = {"user_id": user_id, **data}
        with httpx.Client(timeout=15) as c:
            r = c.post(
                f"{self.base}/subscriptions",
                params={"on_conflict": "user_id"},
                headers={**self.headers, "Prefer": "return=representation"},
                json=row,
            )
            r.raise_for_status()
            return r.json()[0]

    def set_status(self, user_id: str, status: str) -> dict[str, Any]:
        return self.upsert(
            user_id,
            {
                "status": status,
                "updated_at": datetime.now(UTC).isoformat(),
            },
        )
