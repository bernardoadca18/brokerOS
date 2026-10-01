"""Opportunity model for CRM functionality."""
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

# Opportunity stage enum
OpportunityStage = Enum(
    "qualification",
    "proposal",
    "negotiation",
    "won",
    "lost",
    name="opportunity_stage",
)

# Product type enum
ProductType = Enum(
    "vehicle_insurance",
    "consortium",
    name="product_type",
)


class Opportunity(Base):
    """Opportunity model for sales pipeline tracking."""

    __tablename__ = "opportunities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lead_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,  # One-to-one: a lead can only have one opportunity
    )

    # Opportunity details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(
        ProductType, nullable=False, default="vehicle_insurance"
    )
    stage: Mapped[str] = mapped_column(
        OpportunityStage, nullable=False, default="qualification", index=True
    )

    # Financial information
    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Closure information
    lost_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Additional information
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="opportunities"
    )
    owner: Mapped["User | None"] = relationship("User", back_populates="owned_opportunities")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="opportunities")
    lead: Mapped["Lead | None"] = relationship("Lead", back_populates="opportunity")

    __table_args__ = (
        Index("ix_opportunities_org_stage", "organization_id", "stage"),
        Index("ix_opportunities_org_owner", "organization_id", "owner_id"),
        Index("ix_opportunities_org_created", "organization_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Opportunity {self.title} ({self.stage})>"
