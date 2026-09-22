"""Profile schemas (PRD §7)."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileOut(BaseModel):
    id: str
    email: str | None = None
    full_name: str | None = None
    company_name: str | None = None
    company_address: str | None = None
    company_postcode: str | None = None
    company_phone: str | None = None
    logo_path: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    company_name: str | None = Field(default=None, max_length=200)
    company_address: str | None = Field(default=None, max_length=500)
    company_postcode: str | None = Field(default=None, max_length=20)
    company_phone: str | None = Field(default=None, max_length=50)
