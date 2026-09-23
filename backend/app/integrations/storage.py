"""Supabase Storage access — service role only, server-side (PRD §14).

Buckets:
  company-assets  — logos (owner write via backend, public read)
  rams-documents  — generated files (backend only; users get signed URLs)
"""

from dataclasses import dataclass

import httpx

from app.core.config import get_settings

COMPANY_ASSETS_BUCKET = "company-assets"
RAMS_DOCUMENTS_BUCKET = "rams-documents"

# Logo constraints
LOGO_ALLOWED_MIME = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}
LOGO_MAX_BYTES = 2 * 1024 * 1024


class StorageError(Exception):
    pass


@dataclass
class StorageClient:
    base: str
    headers: dict[str, str]

    @classmethod
    def from_settings(cls) -> "StorageClient":
        s = get_settings()
        return cls(
            base=f"{s.supabase_url}/storage/v1",
            headers={
                "apikey": s.supabase_service_role_key,
                "Authorization": f"Bearer {s.supabase_service_role_key}",
            },
        )

    def upload(self, bucket: str, path: str, data: bytes, content_type: str) -> str:
        """Upload (upsert). Returns the storage path."""
        with httpx.Client(timeout=30) as c:
            r = c.post(
                f"{self.base}/object/{bucket}/{path}",
                headers={**self.headers, "Content-Type": content_type, "x-upsert": "true"},
                content=data,
            )
        if r.status_code not in (200, 201):
            raise StorageError(f"Upload failed ({r.status_code}): {r.text[:200]}")
        return path

    def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """Short-lived download URL (default 1h). Frontend opens it directly."""
        with httpx.Client(timeout=15) as c:
            r = c.post(
                f"{self.base}/object/sign/{bucket}/{path}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"expiresIn": expires_in},
            )
        if r.status_code != 200:
            raise StorageError(f"Signed URL failed ({r.status_code}): {r.text[:200]}")
        return r.json()["signedURL"]

    def remove(self, bucket: str, paths: list[str]) -> None:
        """Best-effort delete (used for orphan cleanup). Never raises."""
        try:
            with httpx.Client(timeout=15) as c:
                c.delete(
                    f"{self.base}/object/{bucket}",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json={"prefixes": paths},
                )
        except Exception:
            pass


def rams_doc_path(user_id: str, rams_id: str, kind: str) -> str:
    """Predictable path convention (PRD §14): {user_id}/{rams_id}/rams.{ext}."""
    ext = "docx" if kind == "docx" else "pdf"
    return f"{user_id}/{rams_id}/rams.{ext}"
