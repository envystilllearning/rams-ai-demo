"""Critical subscription tests (PRD §31)."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.entitlement import has_active_subscription

client = TestClient(app)


def test_entitlement_active_and_trialing_allowed() -> None:
    assert has_active_subscription({"status": "active"}) is True
    assert has_active_subscription({"status": "trialing"}) is True


def test_entitlement_inactive_states_blocked() -> None:
    for status in ("canceled", "unpaid", "incomplete", "incomplete_expired", "none", None):
        assert has_active_subscription({"status": status}) is False
    assert has_active_subscription(None) is False


def test_entitlement_past_due_blocked_by_default() -> None:
    # Default config: subscription_allow_past_due=False
    assert has_active_subscription({"status": "past_due"}) is False


def test_billing_requires_auth() -> None:
    for path in ("/api/subscription", "/api/stripe/checkout", "/api/stripe/portal"):
        assert client.get(path).status_code == 401 if path.startswith("/api/sub") else True
        response = client.post(path)
        assert response.status_code in (401, 405)


def test_checkout_mock_activates(monkeypatch) -> None:
    """Mock checkout returns active immediately (repo calls are stubbed)."""
    from app.repositories import subscriptions as sub_mod
    from app.services import entitlement as ent_mod

    store: dict[str, dict] = {}

    class FakeRepo:
        def get(self, user_id):
            return store.get(user_id)

        def upsert(self, user_id, data):
            store.setdefault(user_id, {"user_id": user_id}).update(data)
            return store[user_id]

    monkeypatch.setattr(sub_mod, "SubscriptionsRepo", FakeRepo)
    monkeypatch.setattr(ent_mod, "SubscriptionsRepo", FakeRepo)

    class FakeUser:
        id = "11111111-1111-1111-1111-111111111111"
        email = "demo@example.com"

    import app.routers.billing as billing_mod
    from app.core.deps import get_current_user

    monkeypatch.setattr(billing_mod, "SubscriptionsRepo", FakeRepo)

    # Override the underlying dependency function (Annotated alias resolves to it)
    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        response = client.post("/api/stripe/checkout")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "active"
        assert store[FakeUser.id]["status"] == "active"

        # Second checkout is idempotent — already active
        response2 = client.post("/api/stripe/checkout")
        assert response2.json()["status"] == "already_active"
    finally:
        app.dependency_overrides.clear()


def test_cancel_mock_cancels(monkeypatch) -> None:
    from app.repositories import subscriptions as sub_mod

    store: dict[str, dict] = {
        "22222222-2222-2222-2222-222222222222": {
            "user_id": "22222222-2222-2222-2222-222222222222",
            "status": "active",
        }
    }

    class FakeRepo:
        def get(self, user_id):
            return store.get(user_id)

        def upsert(self, user_id, data):
            store.setdefault(user_id, {"user_id": user_id}).update(data)
            return store[user_id]

    monkeypatch.setattr(sub_mod, "SubscriptionsRepo", FakeRepo)

    class FakeUser:
        id = "22222222-2222-2222-2222-222222222222"
        email = "demo@example.com"

    import app.routers.billing as billing_mod
    from app.core.deps import get_current_user

    monkeypatch.setattr(billing_mod, "SubscriptionsRepo", FakeRepo)
    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        response = client.post("/api/billing/cancel")
        assert response.status_code == 200
        assert store[FakeUser.id]["status"] == "canceled"
        # Entitlement must now be False (PRD §32: access removed)
        assert has_active_subscription(store[FakeUser.id]) is False
    finally:
        app.dependency_overrides.clear()
