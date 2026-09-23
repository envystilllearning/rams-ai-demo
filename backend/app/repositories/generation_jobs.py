"""Generation jobs repository — one active job per RAMS (§44)."""

from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.config import get_settings


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


class GenerationJobsRepo:
    def __init__(self) -> None:
        s = get_settings()
        self.base = f"{s.supabase_url}/rest/v1"
        self.headers = {
            "apikey": s.supabase_service_role_key,
            "Authorization": f"Bearer {s.supabase_service_role_key}",
            "Content-Type": "application/json",
        }

    def active_for_rams(self, user_id: str, rams_id: str) -> dict | None:
        """Return a pending/running job for this RAMS, if any."""
        with httpx.Client(timeout=15) as c:
            r = c.get(
                f"{self.base}/generation_jobs",
                params={
                    "select": "*",
                    "user_id": f"eq.{user_id}",
                    "rams_id": f"eq.{rams_id}",
                    "status": "in.(pending,running)",
                },
                headers=self.headers,
            )
            r.raise_for_status()
            rows = r.json()
            return rows[0] if rows else None

    def create(self, user_id: str, rams_id: str) -> dict[str, Any]:
        with httpx.Client(timeout=15) as c:
            r = c.post(
                f"{self.base}/generation_jobs",
                headers={**self.headers, "Prefer": "return=representation"},
                json={
                    "user_id": user_id,
                    "rams_id": rams_id,
                    "status": "pending",
                    "attempts": 0,
                },
            )
            # Partial unique index (§44) may raise 409 → duplicate job
            if r.status_code == 409:
                raise ValueError("A generation is already running for this RAMS")
            r.raise_for_status()
            return r.json()[0]

    def mark(self, job_id: str, patch: dict[str, Any]) -> None:
        with httpx.Client(timeout=15) as c:
            r = c.patch(
                f"{self.base}/generation_jobs",
                params={"id": f"eq.{job_id}"},
                headers=self.headers,
                json=patch,
            )
            r.raise_for_status()
