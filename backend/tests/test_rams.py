"""RAMS CRUD tests: validation, ownership isolation (PRD §31/§48)."""

from fastapi.testclient import TestClient

from app.main import app
from app.routers.rams import _new_document_number

client = TestClient(app)

VALID_PAYLOAD = {
    "project_name": "Riverside Warehouse Fit-Out",
    "work_description": "Internal partition installation and electrical coordination.",
}


class FakeUserA:
    id = "aaaaaaaa-1111-1111-1111-111111111111"
    email = "a@example.com"


class FakeUserB:
    id = "bbbbbbbb-2222-2222-2222-222222222222"
    email = "b@example.com"


class FakeRamsStore:
    """In-memory stand-in backed by real RamsRepo logic paths."""

    def __init__(self):
        self.rows: dict[str, dict] = {}

    def create(self, user_id, data):
        rid = f"ramsid-{len(self.rows) + 1}"
        row = {"id": rid, "user_id": user_id, "status": "draft", **data}
        self.rows[rid] = row
        return row

    def get(self, user_id, rams_id):
        row = self.rows.get(rams_id)
        return row if row and row["user_id"] == user_id else None

    def list_for_user(self, user_id, limit=50, offset=0):
        items = [r for r in self.rows.values() if r["user_id"] == user_id]
        return items[offset : offset + limit], len(items)

    def delete(self, user_id, rams_id):
        row = self.get(user_id, rams_id)
        if row:
            del self.rows[rams_id]
            return True
        return False


def test_document_number_format() -> None:
    num = _new_document_number()
    assert num.startswith("RAMS-")
    assert len(num) == len("RAMS-") + 8


def test_create_validation_rejects_short_payload() -> None:
    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUserA()
    try:
        # project_name too short + work_description missing
        r = client.post("/api/rams", json={"project_name": "ab"})
        assert r.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_crud_and_ownership_isolation(monkeypatch) -> None:
    from app.core.deps import get_current_user

    store = FakeRamsStore()
    monkeypatch.setattr("app.routers.rams.RamsRepo", lambda: store)

    app.dependency_overrides[get_current_user] = lambda: FakeUserA()
    try:
        # Create as user A
        r = client.post("/api/rams", json=VALID_PAYLOAD)
        assert r.status_code == 201
        body = r.json()
        rams_id = body["id"]
        assert body["document_number"].startswith("RAMS-")
        assert body["status"] == "draft"

        # List shows exactly one
        r = client.get("/api/rams")
        assert r.status_code == 200
        assert r.json()["total"] == 1
    finally:
        app.dependency_overrides.clear()

    # User B cannot see or delete A's RAMS (Risk 5)
    app.dependency_overrides[get_current_user] = lambda: FakeUserB()
    try:
        r = client.get(f"/api/rams/{rams_id}")
        assert r.status_code == 404
        r = client.delete(f"/api/rams/{rams_id}")
        assert r.status_code == 404
        r = client.get("/api/rams")
        assert r.json()["total"] == 0
    finally:
        app.dependency_overrides.clear()

    # Owner can still fetch and delete
    app.dependency_overrides[get_current_user] = lambda: FakeUserA()
    try:
        r = client.get(f"/api/rams/{rams_id}")
        assert r.status_code == 200
        r = client.delete(f"/api/rams/{rams_id}")
        assert r.status_code == 204
        assert store.rows == {}
    finally:
        app.dependency_overrides.clear()


def test_repo_ownership_scoping_in_memory() -> None:
    """Direct repo-level isolation sanity check."""
    store = FakeRamsStore()
    store.create(FakeUserA.id, {"project_name": "A project"})
    assert store.get(FakeUserB.id, "ramsid-1") is None
    assert store.get(FakeUserA.id, "ramsid-1") is not None
