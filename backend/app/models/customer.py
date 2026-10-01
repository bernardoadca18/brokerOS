"""Customer model for CRM functionality."""
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

# Customer type enum
CustomerType = Enum(
    "individual",
    "company",
    name="customer_type",
)


class Customer(Base):
    """Customer model for converted leads and direct customers."""

    __tablename__ = "customers"

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

    # Customer information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_type: Mapped[str] = mapped_column(
        CustomerType, nullable=False, default="individual"
    )

    # Contact information
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

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
        "Organization", back_populates="customers"
    )
    owner: Mapped["User | None"] = relationship("User", back_populates="owned_customers")
    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity", back_populates="customer"
    )

    __table_args__ = (
        Index("ix_customers_org_owner", "organization_id", "owner_id"),
        Index("ix_customers_org_created", "organization_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Customer {self.name} ({self.customer_type})>"
