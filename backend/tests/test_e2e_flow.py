"""End-to-end happy path (PRD §32, in-process with fakes):

subscribe (mock) → create RAMS → generate (mock AI + fake storage) →
download DOCX + PDF → delete → verify cleanup.

Plus the sad path: inactive subscription blocks generation.
"""

import io
import zipfile

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

USER_ID = "e2e00000-0000-0000-0000-000000000000"
EMAIL = "e2e@example.com"


class Store:
    """Shared in-memory backend: subscriptions, rams, jobs, storage."""

    def __init__(self):
        self.subs: dict = {}
        self.rams: dict = {}
        self.jobs: dict = {}
        self.files: dict = {}
        self.removed: list = []


def install_fakes(monkeypatch, store: Store):
    import app.routers.billing as billing_mod
    import app.routers.documents as doc_mod
    import app.routers.profile as profile_mod
    import app.routers.rams as rams_mod
    import app.services.entitlement as ent_mod
    import app.services.generation as gen_mod
    from app.core.deps import get_current_user

    class FakeUser:
        id = USER_ID
        email = EMAIL

    class FakeSubsRepo:
        def get(self, uid):
            return store.subs.get(uid)

        def upsert(self, uid, data):
            store.subs.setdefault(uid, {"user_id": uid}).update(data)
            return store.subs[uid]

    class FakeRamsRepo:
        def get(self, uid, rid):
            row = store.rams.get(rid)
            return row if row and row["user_id"] == uid else None

        def create(self, uid, data):
            rid = f"rams-e2e-{len(store.rams) + 1}"
            row = {"id": rid, "user_id": uid, "status": "draft", **data}
            store.rams[rid] = row
            return row

        def update(self, uid, rid, data):
            row = self.get(uid, rid)
            if row:
                row.update(data)
            return row

        def delete(self, uid, rid):
            row = self.get(uid, rid)
            if row:
                del store.rams[rid]
                return True
            return False

        def list_for_user(self, uid, limit=50, offset=0):
            items = [r for r in store.rams.values() if r["user_id"] == uid]
            return items[offset : offset + limit], len(items)

    class FakeJobsRepo:
        def active_for_rams(self, uid, rid):
            return None

        def create(self, uid, rid):
            job = {"id": "job-e2e"}
            store.jobs[rid] = job
            return job

        def mark(self, jid, patch):
            pass

    class FakeProfilesRepo:
        def get(self, uid):
            return {
                "id": uid,
                "email": EMAIL,
                "company_name": "E2E Builders Ltd",
                "full_name": "E2E Tester",
            }

        def upsert(self, uid, email, data):
            return {"id": uid, "email": email, **data}

        def update(self, uid, data):
            return {"id": uid, "email": EMAIL, **data}

    class FakeStorage:
        @classmethod
        def from_settings(cls):
            return cls()

        def upload(self, bucket, path, data, content_type):
            assert len(data) > 1000
            store.files[path] = {"bucket": bucket, "size": len(data)}
            return path

        def create_signed_url(self, bucket, path, expires_in=3600):
            assert path in store.files
            return f"https://signed.example/{bucket}/{path}"

        def remove(self, bucket, paths):
            for p in paths:
                store.files.pop(p, None)
                store.removed.append(p)

    for mod in (billing_mod, doc_mod, profile_mod, rams_mod, gen_mod, ent_mod):
        for name, cls in (
            ("SubscriptionsRepo", FakeSubsRepo),
            ("RamsRepo", FakeRamsRepo),
            ("GenerationJobsRepo", FakeJobsRepo),
            ("ProfilesRepo", FakeProfilesRepo),
            ("StorageClient", FakeStorage),
        ):
            if hasattr(mod, name):
                monkeypatch.setattr(mod, name, cls)

    app.dependency_overrides[get_current_user] = lambda: FakeUser()


def test_full_happy_path(monkeypatch) -> None:
    store = Store()
    install_fakes(monkeypatch, store)
    try:
        # 1. Subscribe (mock activates instantly)
        r = client.post("/api/stripe/checkout")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

        # 2. Subscription state reflects entitlement
        r = client.get("/api/subscription")
        assert r.json()["can_generate"] is True

        # 3. Create RAMS draft
        r = client.post(
            "/api/rams",
            json={
                "project_name": "E2E Warehouse Project",
                "work_description": "Full internal fit-out including partitions and electrics.",
                "known_hazards": "Dust. Narrow access.",
            },
        )
        assert r.status_code == 201
        rams_id = r.json()["id"]
        assert r.json()["status"] == "draft"

        # 4. Generate (mock AI → DOCX → PDF → fake storage)
        r = client.post(f"/api/rams/{rams_id}/generate")
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "ready"

        # 5. Both files persisted
        assert len(store.files) == 2
        row = client.get(f"/api/rams/{rams_id}").json()
        assert row["status"] == "ready"
        assert row["docx_path"].endswith(".docx")
        assert row["pdf_path"].endswith(".pdf")

        # 6. Signed downloads work
        for kind in ("docx", "pdf"):
            r = client.get(f"/api/rams/{rams_id}/documents/{kind}/download")
            assert r.status_code == 200
            assert r.json()["url"].startswith("https://signed.example/")

        # 7. On-demand builds still work
        r = client.get(f"/api/rams/{rams_id}/documents/docx")
        assert r.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        assert "word/document.xml" in zf.namelist()
        r = client.get(f"/api/rams/{rams_id}/documents/pdf")
        assert r.status_code == 200
        assert r.content[:5] == b"%PDF-"

        # 8. Second RAMS reuses company profile (implicitly via generation)
        r = client.post(
            "/api/rams",
            json={
                "project_name": "Second E2E Project",
                "work_description": "External cladding replacement works package.",
            },
        )
        assert r.status_code == 201
        second_id = r.json()["id"]
        r = client.post(f"/api/rams/{second_id}/generate")
        assert r.json()["status"] == "ready"

        # 9. Cancel removes generation access (entitlement end)
        r = client.post("/api/billing/cancel")
        assert r.status_code == 200
        assert client.get("/api/subscription").json()["can_generate"] is False

        r = client.post(f"/api/rams/{second_id}/generate")
        assert r.status_code == 403
        assert r.json()["code"] == "SUBSCRIPTION_REQUIRED"

        # 10. Delete cleans stored files
        r = client.delete(f"/api/rams/{rams_id}")
        assert r.status_code == 204
        assert len(store.files) == 2  # second RAMS files remain
        assert any("rams-e2e-1" in p for p in store.removed)
    finally:
        app.dependency_overrides.clear()


def test_sad_path_no_subscription(monkeypatch) -> None:
    """Fresh user without subscription: blocked at generation, allowed to draft."""
    store = Store()
    install_fakes(monkeypatch, store)
    try:
        r = client.get("/api/subscription")
        assert r.json()["can_generate"] is False

        r = client.post(
            "/api/rams",
            json={
                "project_name": "Blocked Project",
                "work_description": "Works that cannot be generated yet.",
            },
        )
        assert r.status_code == 201
        rams_id = r.json()["id"]

        r = client.post(f"/api/rams/{rams_id}/generate")
        assert r.status_code == 403
        assert r.json()["code"] == "SUBSCRIPTION_REQUIRED"
        assert len(store.files) == 0  # nothing persisted
    finally:
        app.dependency_overrides.clear()
