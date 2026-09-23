"""RAMS schemas (PRD §8, §9)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RamsCreate(BaseModel):
    """Step 1-3 form payload. Validation mirrors the 4-step wizard."""

    # Step 1 — Project
    project_name: str = Field(min_length=3, max_length=300)
    site_address: str | None = Field(default=None, max_length=500)
    client_name: str | None = Field(default=None, max_length=300)
    project_reference: str | None = Field(default=None, max_length=100)
    start_date: str | None = Field(default=None, max_length=20)
    planned_duration: str | None = Field(default=None, max_length=100)

    # Step 2 — Work
    work_description: str = Field(min_length=10, max_length=5000)
    work_location: str | None = Field(default=None, max_length=500)
    materials: str | None = Field(default=None, max_length=2000)
    equipment: str | None = Field(default=None, max_length=2000)
    plant: str | None = Field(default=None, max_length=2000)
    tools: str | None = Field(default=None, max_length=2000)
    personnel: str | None = Field(default=None, max_length=2000)
    ppe: str | None = Field(default=None, max_length=2000)

    # Step 3 — Controls
    known_hazards: str | None = Field(default=None, max_length=3000)
    site_restrictions: str | None = Field(default=None, max_length=2000)
    existing_controls: str | None = Field(default=None, max_length=3000)
    emergency_info: str | None = Field(default=None, max_length=2000)
    additional_notes: str | None = Field(default=None, max_length=2000)


class RamsOut(BaseModel):
    id: str
    document_number: str | None = None
    project_name: str
    site_address: str | None = None
    client_name: str | None = None
    project_reference: str | None = None
    status: str
    input_data: dict[str, Any]
    generated_data: dict[str, Any] | None = None
    docx_path: str | None = None
    pdf_path: str | None = None
    generation_error: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RamsListOut(BaseModel):
    items: list[RamsOut]
    total: int
