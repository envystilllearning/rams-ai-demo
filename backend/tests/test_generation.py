"""AI generation tests (PRD §31): success, blocked, duplicate, failure safety."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.integrations.ai import AiError, MockAiProvider
from app.main import app
from app.schemas.ai_output import AiRamsOutput, risk_score

client = TestClient(app)

FORM = {
    "project_name": "Riverside Warehouse Fit-Out",
    "work_description": "Internal partition installation and electrical coordination.",
    "known_hazards": "Narrow access routes. Dust from cutting.",
}


def test_risk_score_matrix() -> None:
    assert risk_score(1, 1) == 1
    assert risk_score(3, 4) == 12
    assert risk_score(5, 5) == 25
    with pytest.raises(ValueError):
        risk_score(0, 3)
    with pytest.raises(ValueError):
        risk_score(3, 6)


def test_mock_output_validates() -> None:
    out = MockAiProvider().generate(FORM)
    assert isinstance(out, AiRamsOutput)
    assert len(out.hazards) >= 1
    for h in out.hazards:
        assert h.initial_risk_score == h.initial_likelihood * h.initial_severity
        assert h.residual_risk_score == h.residual_likelihood * h.residual_severity
    assert len(out.sequence_of_works) >= 1
    assert len(out.ppe) >= 1


def test_invalid_ai_output_rejected() -> None:
    with pytest.raises(ValidationError):
        AiRamsOutput.model_validate({"project_summary": "too short"})


class FakeUser:
    id = "33333333-3333-3333-3333-333333333333"
    email = "gen@example.com"


def _patch_pipeline(monkeypatch, *, rams_row, entitled=True, active_job=None):
    import app.services.generation as gen_mod
    from app.repositories import rams as rams_mod

    store = {"rams": rams_row, "jobs": [], "updated": []}

    class FakeRamsRepo:
        def get(self, user_id, rams_id):
            return store["rams"] if store["rams"] and store["rams"]["id"] == rams_id else None

        def update(self, user_id, rams_id, data):
            store["updated"].append(data)
            if store["rams"]:
                store["rams"].update(data)
            return store["rams"]

    class FakeJobsRepo:
        def active_for_rams(self, user_id, rams_id):
            return active_job

        def create(self, user_id, rams_id):
            job = {"id": "job-1"}
            store["jobs"].append(job)
            return job

        def mark(self, job_id, patch):
            pass

    monkeypatch.setattr(gen_mod, "RamsRepo", FakeRamsRepo)
    monkeypatch.setattr(gen_mod, "GenerationJobsRepo", FakeJobsRepo)
    monkeypatch.setattr(rams_mod, "RamsRepo", FakeRamsRepo)
    monkeypatch.setattr(gen_mod, "check_entitlement", lambda uid: entitled)

    from app.core.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    return store


def teardown_override():
    app.dependency_overrides.clear()


def test_generate_success(monkeypatch) -> None:
    store = _patch_pipeline(
        monkeypatch,
        rams_row={"id": "rams-1", "input_data": FORM, "status": "draft"},
    )
    try:
        r = client.post("/api/rams/rams-1/generate")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "generated"
        assert body["generated_hazards"] >= 1
        assert body["provider"] == "mock"
        # RAMS persisted with generated content
        assert store["rams"]["status"] == "generated"
        assert store["rams"]["generated_data"]["project_summary"]
    finally:
        teardown_override()


def test_generate_requires_subscription(monkeypatch) -> None:
    _patch_pipeline(
        monkeypatch,
        rams_row={"id": "rams-1", "input_data": FORM, "status": "draft"},
        entitled=False,
    )
    try:
        r = client.post("/api/rams/rams-1/generate")
        assert r.status_code == 403
        assert r.json()["code"] == "SUBSCRIPTION_REQUIRED"
    finally:
        teardown_override()


def test_generate_404_for_missing_rams(monkeypatch) -> None:
    _patch_pipeline(monkeypatch, rams_row=None)
    try:
        r = client.post("/api/rams/nope/generate")
        assert r.status_code == 404
        assert r.json()["code"] == "DOCUMENT_NOT_FOUND"
    finally:
        teardown_override()


def test_generate_blocks_duplicate(monkeypatch) -> None:
    _patch_pipeline(
        monkeypatch,
        rams_row={"id": "rams-1", "input_data": FORM, "status": "generating"},
        active_job={"id": "job-running", "status": "running"},
    )
    try:
        r = client.post("/api/rams/rams-1/generate")
        assert r.status_code == 409
        assert r.json()["code"] == "GENERATION_IN_PROGRESS"
    finally:
        teardown_override()


def test_generate_ai_failure_marks_failed(monkeypatch) -> None:
    store = _patch_pipeline(
        monkeypatch,
        rams_row={"id": "rams-1", "input_data": FORM, "status": "draft"},
    )
    import app.services.generation as gen_mod

    class FailingProvider:
        name = "failing"

        def generate(self, form_input):
            raise AiError("AI_GENERATION_FAILED", "boom")

    monkeypatch.setattr(gen_mod, "get_ai_provider", lambda: FailingProvider())
    try:
        r = client.post("/api/rams/rams-1/generate")
        assert r.status_code == 502
        assert r.json()["code"] == "AI_GENERATION_FAILED"
        # No partial document: status failed, no generated content
        assert store["rams"]["status"] == "failed"
        assert "generated_data" not in store["rams"] or not store["rams"].get("generated_data")
        assert store["rams"]["generation_error"]
    finally:
        teardown_override()
