"""Pydantic schemas for Customer API."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# Enums as literals for type safety
CustomerTypeLiteral = Literal["individual", "company"]


class CustomerBase(BaseModel):
    """Base schema for Customer."""

    name: str = Field(..., min_length=1, max_length=255)
    customer_type: CustomerTypeLiteral = "individual"
    email: EmailStr | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=2000)


class CustomerCreate(CustomerBase):
    """Schema for creating a Customer."""

    owner_id: UUID | None = None  # Optional: Admin/Manager can assign, Sales auto-assigns


class CustomerUpdate(BaseModel):
    """Schema for updating a Customer."""

    name: str | None = Field(None, min_length=1, max_length=255)
    customer_type: CustomerTypeLiteral | None = None
    email: EmailStr | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=2000)
    owner_id: UUID | None = None


class CustomerResponse(BaseModel):
    """Schema for Customer response."""

    id: UUID
    organization_id: UUID
    owner_id: UUID | None
    name: str
    customer_type: str
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    """Schema for paginated Customer list response."""

    items: list[CustomerResponse]
    total: int
    limit: int
    offset: int
