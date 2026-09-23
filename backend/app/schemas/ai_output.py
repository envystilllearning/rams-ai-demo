"""Structured AI output schemas (PRD §11).

The AI must return JSON matching AiRamsOutput. Anything invalid is
rejected BEFORE document generation — never partial documents.
"""

from pydantic import BaseModel, Field


class AiHazard(BaseModel):
    hazard: str = Field(min_length=3, max_length=500)
    who_might_be_harmed: str = Field(min_length=3, max_length=300)
    existing_controls: str = Field(min_length=3, max_length=1000)
    initial_likelihood: int = Field(ge=1, le=5)
    initial_severity: int = Field(ge=1, le=5)
    initial_risk_score: int = Field(ge=1, le=25)
    additional_controls: str = Field(min_length=3, max_length=1000)
    residual_likelihood: int = Field(ge=1, le=5)
    residual_severity: int = Field(ge=1, le=5)
    residual_risk_score: int = Field(ge=1, le=25)


class AiMethodStatement(BaseModel):
    preparation: str = Field(min_length=10, max_length=3000)
    execution: str = Field(min_length=10, max_length=5000)
    completion: str = Field(min_length=10, max_length=3000)


class AiRamsOutput(BaseModel):
    project_summary: str = Field(min_length=10, max_length=2000)
    scope_of_work: str = Field(min_length=10, max_length=3000)
    sequence_of_works: list[str] = Field(min_length=1, max_length=20)
    hazards: list[AiHazard] = Field(min_length=1, max_length=20)
    method_statement: AiMethodStatement
    emergency_procedure: str = Field(min_length=10, max_length=2000)
    environmental_controls: str = Field(min_length=10, max_length=2000)
    ppe: list[str] = Field(min_length=1, max_length=20)


def risk_score(likelihood: int, severity: int) -> int:
    """Risk matrix: likelihood (1-5) × severity (1-5)."""
    if not (1 <= likelihood <= 5 and 1 <= severity <= 5):
        raise ValueError("likelihood and severity must be 1-5")
    return likelihood * severity
