import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import GUID, Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.lead import Lead
    from app.models.customer import Customer
    from app.models.opportunity import Opportunity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import GUID, Base

if TYPE_CHECKING:
    from app.models.organization import Organization

RoleType = Literal["admin", "manager", "sales"]


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_user_org_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="sales")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")

    # CRM entity relationships
    owned_leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="owner")
    owned_customers: Mapped[list["Customer"]] = relationship("Customer", back_populates="owner")
    owned_opportunities: Mapped[list["Opportunity"]] = relationship("Opportunity", back_populates="owner")
