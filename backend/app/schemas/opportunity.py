"""Pydantic schemas for Opportunity API."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Enums as literals for type safety
OpportunityStageLiteral = Literal["qualification", "proposal", "negotiation", "won", "lost"]
ProductTypeLiteral = Literal["vehicle_insurance", "consortium"]


class OpportunityBase(BaseModel):
    """Base schema for Opportunity."""

    title: str = Field(..., min_length=1, max_length=255)
    product_type: ProductTypeLiteral
    stage: OpportunityStageLiteral = "qualification"
    amount: Decimal | None = Field(None, ge=0)
    expected_close_date: date | None = None
    lost_reason: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)


class OpportunityCreate(OpportunityBase):
    """Schema for creating an Opportunity."""

    customer_id: UUID
    lead_id: UUID | None = None  # Optional link to originating lead
    owner_id: UUID | None = None  # Optional: Admin/Manager can assign, Sales auto-assigns


class OpportunityUpdate(BaseModel):
    """Schema for updating an Opportunity."""

    title: str | None = Field(None, min_length=1, max_length=255)
    product_type: ProductTypeLiteral | None = None
    stage: OpportunityStageLiteral | None = None
    amount: Decimal | None = Field(None, ge=0)
    expected_close_date: date | None = None
    lost_reason: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)
    owner_id: UUID | None = None
    customer_id: UUID | None = None


class OpportunityResponse(BaseModel):
    """Schema for Opportunity response."""

    id: UUID
    organization_id: UUID
    owner_id: UUID | None
    customer_id: UUID
    lead_id: UUID | None
    title: str
    product_type: str
    stage: str
    amount: Decimal | None
    expected_close_date: date | None
    lost_reason: str | None
    closed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OpportunityListResponse(BaseModel):
    """Schema for paginated Opportunity list response."""

    items: list[OpportunityResponse]
    total: int
    limit: int
    offset: int
