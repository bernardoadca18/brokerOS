"""Lead model for CRM functionality."""
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

# Lead source enum
LeadSource = Enum(
    "manual",
    "website",
    "referral",
    "whatsapp",
    "campaign",
    "other",
    name="lead_source",
)

# Lead status enum
LeadStatus = Enum(
    "new",
    "contacted",
    "qualified",
    "unqualified",
    "converted",
    name="lead_status",
)

# Product interest enum
ProductInterest = Enum(
    "vehicle_insurance",
    "consortium",
    name="product_interest",
)


class Lead(Base):
    """Lead model for capturing potential customers."""

    __tablename__ = "leads"

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

    # Contact information
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Lead details
    product_interest: Mapped[str] = mapped_column(
        ProductInterest, nullable=False, default="vehicle_insurance"
    )
    source: Mapped[str] = mapped_column(
        LeadSource, nullable=False, default="manual"
    )
    status: Mapped[str] = mapped_column(
        LeadStatus, nullable=False, default="new", index=True
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
        "Organization", back_populates="leads"
    )
    owner: Mapped["User | None"] = relationship("User", back_populates="owned_leads")
    opportunity: Mapped["Opportunity | None"] = relationship(
        "Opportunity", back_populates="lead", uselist=False
    )

    __table_args__ = (
        Index("ix_leads_org_status", "organization_id", "status"),
        Index("ix_leads_org_owner", "organization_id", "owner_id"),
        Index("ix_leads_org_created", "organization_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Lead {self.full_name} ({self.status})>"
