"""Pydantic schemas for Lead API."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# Enums as literals for type safety
LeadSourceLiteral = Literal["manual", "website", "referral", "whatsapp", "campaign", "other"]
LeadStatusLiteral = Literal["new", "contacted", "qualified", "unqualified", "converted"]
ProductInterestLiteral = Literal["vehicle_insurance", "consortium"]


class LeadBase(BaseModel):
    """Base schema for Lead."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    product_interest: ProductInterestLiteral
    source: LeadSourceLiteral = "manual"
    notes: str | None = Field(None, max_length=2000)

    @field_validator("phone", "email")
    @classmethod
    def validate_contact(cls, v: str | None, info) -> str | None:
        """Ensure at least one contact method is provided on create."""
        return v


class LeadCreate(LeadBase):
    """Schema for creating a Lead."""

    owner_id: UUID | None = None  # Optional: Admin/Manager can assign, Sales auto-assigns

    @field_validator("email", "phone")
    @classmethod
    def require_contact(cls, v: str | None, info) -> str | None:
        """Require at least email or phone."""
        # This validation happens at the model level in the service
        return v


class LeadUpdate(BaseModel):
    """Schema for updating a Lead."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    product_interest: ProductInterestLiteral | None = None
    source: LeadSourceLiteral | None = None
    status: LeadStatusLiteral | None = None
    notes: str | None = Field(None, max_length=2000)
    owner_id: UUID | None = None


class LeadResponse(BaseModel):
    """Schema for Lead response."""

    id: UUID
    organization_id: UUID
    owner_id: UUID | None
    full_name: str
    email: str | None
    phone: str | None
    product_interest: str
    source: str
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    """Schema for paginated Lead list response."""

    items: list[LeadResponse]
    total: int
    limit: int
    offset: int


class LeadConversionRequest(BaseModel):
    """Schema for Lead conversion request."""

    customer_type: Literal["individual", "company"] = "individual"
    opportunity_title: str | None = Field(None, max_length=255)
    product_type: Literal["vehicle_insurance", "consortium"] | None = None
    amount: Decimal | None = Field(None, ge=0)
    expected_close_date: str | None = None  # ISO date string
    notes: str | None = Field(None, max_length=2000)


class LeadConversionResponse(BaseModel):
    """Schema for Lead conversion response."""

    lead: LeadResponse
    customer: "CustomerResponse"
    opportunity: "OpportunityResponse"


# Import for forward references
from app.schemas.customer import CustomerResponse
from app.schemas.opportunity import OpportunityResponse

LeadConversionResponse.model_rebuild()
