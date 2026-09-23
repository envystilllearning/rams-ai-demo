"""AI provider abstraction (PRD §11).

`MockAiProvider`       — demo: deterministic structured output from form input.
`OpenRouterProvider`   — real integration; AI_PROVIDER=openrouter + key needed.
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.ai_output import AiRamsOutput, risk_score


class AiError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class AiProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, form_input: dict[str, Any]) -> AiRamsOutput: ...


def _mock_hazards(form_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Build deterministic hazards seeded by the user's known_hazards text."""
    known = (form_input.get("known_hazards") or "").strip()
    first_hint = known.split(".")[0].strip() if known else ""
    work = (form_input.get("work_description") or "the works")[:80]

    def hazard_row(hazard: str, who: str, controls: str, il: int, is_: int, rl: int, rs: int, extra: str) -> dict:
        return {
            "hazard": hazard,
            "who_might_be_harmed": who,
            "existing_controls": controls,
            "initial_likelihood": il,
            "initial_severity": is_,
            "initial_risk_score": risk_score(il, is_),
            "additional_controls": extra,
            "residual_likelihood": rl,
            "residual_severity": rs,
            "residual_risk_score": risk_score(rl, rs),
        }

    rows = [
        hazard_row(
            first_hint or f"Manual handling during {work}",
            "Site operatives and labourers",
            "Manual handling assessment completed; team lifts for loads over 20kg",
            3, 3, 2, 2,
            "Use mechanical aids where practicable; toolbox talk on lifting technique",
        ),
        hazard_row(
            "Slips, trips and falls on site",
            "All persons on site and visitors",
            "Walkways kept clear; cables ramped or buried; good housekeeping",
            3, 2, 2, 1,
            "Daily housekeeping checks by supervisor; report defects immediately",
        ),
        hazard_row(
            "Working with hand and power tools",
            "Operatives using the tools",
            "Tools PAT tested; guards in place; competent operators only",
            2, 3, 1, 3,
            "Pre-use checks recorded; isolate and lock off when changing blades/bits",
        ),
    ]
    return rows


class MockAiProvider(AiProvider):
    name = "mock"

    def generate(self, form_input: dict[str, Any]) -> AiRamsOutput:
        work = form_input.get("work_description") or "the described works"
        location = form_input.get("work_location") or "the work area"
        project = form_input.get("project_name") or "the project"
        emergency = form_input.get("emergency_info") or ""
        ppe_raw = form_input.get("ppe") or "Safety helmet, hi-vis vest, safety boots, gloves, eye protection"

        ppe = [p.strip() for p in str(ppe_raw).replace(";", ",").split(",") if p.strip()][:20] or [
            "Safety helmet",
            "Hi-vis vest",
            "Safety boots",
        ]

        output = {
            "project_summary": (
                f"Risk assessment and method statement for {project}: {work[:200]} "
                f"at {location}."
            ),
            "scope_of_work": f"{work[:1500]}",
            "sequence_of_works": [
                "Mobilise to site, establish welfare and access arrangements",
                "Carry out site induction and review this RAMS with all operatives",
                "Set up work area, barriers, signage and exclusion zones",
                "Execute the works in the planned sequence with supervision",
                "Inspect, snag and hand over completed works to the client",
            ],
            "hazards": _mock_hazards(form_input),
            "method_statement": {
                "preparation": (
                    "Confirm permits and isolations are in place. Brief all operatives "
                    "on this RAMS. Check plant, tools and PPE before starting."
                ),
                "execution": (
                    f"Carry out {work[:500]} in a controlled sequence under competent "
                    "supervision, maintaining exclusion zones and housekeeping throughout."
                ),
                "completion": (
                    "Remove plant and waste from site. Inspect completed work, "
                    "record any defects, and hand over to the client with documentation."
                ),
            },
            "emergency_procedure": (
                emergency
                or "In an emergency: stop work, make the area safe, raise the alarm, "
                "dial 999 if required, and report to the designated assembly point."
            ),
            "environmental_controls": (
                "Segregate waste for recycling; control dust and noise; prevent spills "
                "reaching drains; dispose of waste via licensed carriers."
            ),
            "ppe": ppe,
        }
        return AiRamsOutput.model_validate(output)


SYSTEM_PROMPT = """You are a UK construction health & safety assistant writing a draft
Risk Assessment and Method Statement (RAMS). Return ONLY valid JSON matching
the provided schema — no markdown, no commentary. Likelihood/severity are 1-5
integers; risk scores must equal likelihood × severity. Keep entries concise
and site-practical."""


class OpenRouterProvider(AiProvider):
    """Real OpenRouter integration (OpenAI-compatible). Max 2 attempts."""

    name = "openrouter"
    timeout = 45.0
    max_attempts = 2

    def generate(self, form_input: dict[str, Any]) -> AiRamsOutput:
        s = get_settings()
        if not s.openrouter_api_key:
            raise AiError("AI_GENERATION_FAILED", "OpenRouter API key is not configured")

        schema = AiRamsOutput.model_json_schema()
        user_prompt = (
            "Generate a draft RAMS as JSON for this project.\n"
            f"Form input:\n{json.dumps(form_input, indent=1)[:6000]}"
        )

        last_error: AiError | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                with httpx.Client(timeout=self.timeout) as c:
                    r = c.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {s.openrouter_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": s.openrouter_model,
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt},
                            ],
                            "response_format": {
                                "type": "json_schema",
                                "json_schema": {"name": "rams", "schema": schema, "strict": True},
                            },
                        },
                    )
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"]
                data = json.loads(content)
                return AiRamsOutput.model_validate(data)
            except (httpx.TimeoutException, httpx.HTTPError):
                last_error = AiError(
                    "AI_GENERATION_FAILED",
                    f"AI request failed (attempt {attempt}/{self.max_attempts})",
                )
                if attempt < self.max_attempts:
                    time.sleep(2**attempt)  # exponential backoff
            except (json.JSONDecodeError, KeyError) as exc:
                raise AiError("AI_INVALID_RESPONSE", "AI returned malformed JSON") from exc
            except Exception as exc:  # Pydantic ValidationError included
                raise AiError(
                    "AI_INVALID_RESPONSE",
                    f"AI output failed validation: {exc}",
                ) from exc

        raise last_error or AiError("AI_GENERATION_FAILED", "AI request failed")


def get_ai_provider() -> AiProvider:
    s = get_settings()
    if s.ai_provider.lower() == "openrouter":
        return OpenRouterProvider()
    return MockAiProvider()
