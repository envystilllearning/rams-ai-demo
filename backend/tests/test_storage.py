"""Storage tests (PRD §31): signed downloads, logo guards, orphan cleanup."""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

READY_ROW = {
    "id": "rams-1",
    "document_number": "RAMS-ST1",
    "status": "ready",
    "input_data": {},
    "generated_data": {"hazards": [{"hazard": "x"}]},
    "docx_path": "uid/rams-1/rams.docx",
    "pdf_path": "uid/rams-1/rams.pdf",
}


class FakeUser:
    id = "uid"
    email = "storage@example.com"


def _override(user, rams_row):
    import unittest.mock as mock

    import app.routers.documents as doc_mod
    from app.core.deps import get_current_user

    class FakeRamsRepo:
        def get(self, uid, rid):
            return rams_row if rams_row and rid == "rams-1" else None

    class FakeStorage:
        def __init__(self):
            pass

        @classmethod
        def from_settings(cls):
            return cls()

        def create_signed_url(self, bucket, path, expires_in=3600):
            return f"https://signed.example/{bucket}/{path}?exp={expires_in}"

        def upload(self, bucket, path, data, content_type):
            return path

        def remove(self, bucket, paths):
            pass

    app.dependency_overrides[get_current_user] = lambda: user
    p1 = mock.patch.object(doc_mod, "RamsRepo", FakeRamsRepo)
    p2 = mock.patch.object(doc_mod, "StorageClient", FakeStorage)
    p1.start()
    p2.start()
    return p1, p2


def test_download_endpoint_guards() -> None:
    r = client.get("/api/rams/rams-1/documents/docx/download")
    assert r.status_code == 401

    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        # bad kind
        r = client.get("/api/rams/rams-1/documents/txt/download")
        assert r.status_code == 400

        # missing RAMS
        p1, p2 = _override(FakeUser(), None)
        r = client.get("/api/rams/rams-1/documents/docx/download")
        assert r.status_code == 404
        p1.stop()
        p2.stop()

        # not ready yet
        p1, p2 = _override(FakeUser(), {**READY_ROW, "status": "generated"})
        r = client.get("/api/rams/rams-1/documents/docx/download")
        assert r.status_code == 409
        assert r.json()["code"] == "DOCUMENT_NOT_READY"
        p1.stop()
        p2.stop()
    finally:
        app.dependency_overrides.clear()


def test_download_returns_signed_url() -> None:
    p1, p2 = _override(FakeUser(), READY_ROW)
    try:
        r = client.get("/api/rams/rams-1/documents/pdf/download")
        assert r.status_code == 200
        body = r.json()
        assert body["url"].startswith("https://signed.example/")
        assert "rams.pdf" in body["url"]
        assert body["filename"] == "RAMS-ST1.pdf"
        assert body["expires_in"] == 3600
    finally:
        p1.stop()
        p2.stop()
        app.dependency_overrides.clear()


def test_logo_rejects_bad_mime() -> None:
    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        r = client.post(
            "/api/profile/logo",
            files={"file": ("evil.exe", io.BytesIO(b"MZ..."), "application/x-msdownload")},
        )
        assert r.status_code == 400
        assert r.json()["code"] == "VALIDATION_ERROR"
    finally:
        app.dependency_overrides.clear()


def test_logo_rejects_oversize() -> None:
    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        big = io.BytesIO(b"\x89PNG" + b"0" * (2 * 1024 * 1024 + 1))
        r = client.post(
            "/api/profile/logo",
            files={"file": ("big.png", big, "image/png")},
        )
        assert r.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_rams_doc_path_convention() -> None:
    from app.integrations.storage import rams_doc_path

    assert rams_doc_path("u1", "r1", "docx") == "u1/r1/rams.docx"
    assert rams_doc_path("u1", "r1", "pdf") == "u1/r1/rams.pdf"
