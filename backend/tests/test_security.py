"""Rate limiter + startup validation tests (PRD §15, §27)."""

from fastapi.testclient import TestClient

from app.core.ratelimit import RateLimiter
from app.main import app, lifespan

client = TestClient(app)


def test_limiter_allows_then_blocks() -> None:
    lim = RateLimiter(max_calls=3, window_seconds=60)
    assert lim.allow("u1") is True
    assert lim.allow("u1") is True
    assert lim.allow("u1") is True
    assert lim.allow("u1") is False
    # Other users unaffected
    assert lim.allow("u2") is True


def test_limiter_window_expiry(monkeypatch) -> None:
    import app.core.ratelimit as rl

    lim = RateLimiter(max_calls=1, window_seconds=10)
    now = [1000.0]
    monkeypatch.setattr(rl.time, "monotonic", lambda: now[0])
    assert lim.allow("u") is True
    assert lim.allow("u") is False
    now[0] += 11  # window passes
    assert lim.allow("u") is True


def test_generate_rate_limited(monkeypatch) -> None:
    """429 when the same user exceeds the generation quota."""
    import app.routers.generation as gen_router
    from app.core.deps import get_current_user

    class FakeUser:
        id = "rate-user-1"
        email = "rate@example.com"

    calls = {"n": 0}

    def fake_run(uid, rid):
        calls["n"] += 1
        return {"status": "ready", "rams": {"generated_data": {"hazards": []}}, "provider": "mock"}

    monkeypatch.setattr(gen_router, "run_generation", fake_run)
    # Tiny quota for this test
    import app.core.ratelimit as rl

    monkeypatch.setattr(
        gen_router, "generate_limiter", rl.RateLimiter(max_calls=2, window_seconds=60)
    )
    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        assert client.post("/api/rams/r1/generate").status_code == 200
        assert client.post("/api/rams/r1/generate").status_code == 200
        r = client.post("/api/rams/r1/generate")
        assert r.status_code == 429
        assert r.json()["code"] == "RATE_LIMITED"
        assert calls["n"] == 2  # pipeline never ran the 3rd time
    finally:
        app.dependency_overrides.clear()


def test_lifespan_warns_in_dev(monkeypatch, caplog) -> None:
    """Dev mode: missing keys warn instead of crashing."""
    import asyncio

    import app.main as main_mod

    monkeypatch.setattr(main_mod.settings, "app_env", "development")
    monkeypatch.setattr(main_mod.settings, "supabase_url", "")
    monkeypatch.setattr(main_mod.settings, "supabase_service_role_key", "")

    import logging

    async def run():
        async with lifespan(main_mod.app):
            pass

    with caplog.at_level(logging.WARNING, logger="rams"):
        asyncio.run(run())
    assert any("Missing required environment variables" in m for m in caplog.messages)
