"""PDF tests (PRD §31): valid file, content, endpoint guards."""

import io

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app
from app.services.pdf import build_rams_pdf
from tests.test_documents import FORM, GENERATED, PROFILE

client = TestClient(app)


def test_pdf_is_valid_and_contains_content() -> None:
    data = build_rams_pdf(FORM, GENERATED, PROFILE, "RAMS-PDF0001")
    assert len(data) > 5000
    assert data[:5] == b"%PDF-"

    reader = PdfReader(io.BytesIO(data))
    assert len(reader.pages) >= 2  # cover + content
    text = "\n".join(p.extract_text() or "" for p in reader.pages)

    assert "Riverside Warehouse Fit-Out" in text
    assert "RAMS-PDF0001" in text
    assert "Northbridge Construction Ltd" in text
    assert "Manual handling" in text
    assert "competent person" in text  # disclaimer
    assert "Review and sign-off" in text


def test_pdf_refuses_empty_hazards() -> None:
    with pytest.raises(ValueError):
        build_rams_pdf(FORM, {**GENERATED, "hazards": []}, PROFILE, "RAMS-X")


class FakeUser:
    id = "55555555-5555-5555-5555-555555555555"
    email = "pdf@example.com"


def _override(user, rams_row):
    import unittest.mock as mock

    import app.routers.documents as doc_mod
    from app.core.deps import get_current_user

    class FakeRamsRepo:
        def get(self, uid, rid):
            return rams_row if rams_row and rid == "rams-1" else None

    class FakeProfilesRepo:
        def get(self, uid):
            return PROFILE

    app.dependency_overrides[get_current_user] = lambda: user
    p1 = mock.patch.object(doc_mod, "RamsRepo", FakeRamsRepo)
    p2 = mock.patch.object(doc_mod, "ProfilesRepo", FakeProfilesRepo)
    p1.start()
    p2.start()
    return p1, p2


def test_pdf_endpoint_guards() -> None:
    r = client.get("/api/rams/rams-1/documents/pdf")
    assert r.status_code == 401

    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        p1, p2 = _override(FakeUser(), None)
        assert client.get("/api/rams/rams-1/documents/pdf").status_code == 404
        p1.stop()
        p2.stop()

        p1, p2 = _override(FakeUser(), {"id": "rams-1", "input_data": FORM, "generated_data": None})
        r = client.get("/api/rams/rams-1/documents/pdf")
        assert r.status_code == 409
        assert r.json()["code"] == "DOCUMENT_NOT_READY"
        p1.stop()
        p2.stop()
    finally:
        app.dependency_overrides.clear()


def test_pdf_endpoint_downloads() -> None:
    row = {
        "id": "rams-1",
        "document_number": "RAMS-PDFDL1",
        "input_data": FORM,
        "generated_data": GENERATED,
    }
    p1, p2 = _override(FakeUser(), row)
    try:
        r = client.get("/api/rams/rams-1/documents/pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert "RAMS-PDFDL1.pdf" in r.headers["content-disposition"]
        assert r.content[:5] == b"%PDF-"
    finally:
        p1.stop()
        p2.stop()

        app.dependency_overrides.clear()
