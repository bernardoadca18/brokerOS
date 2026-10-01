import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import GUID, Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.lead import Lead
    from app.models.customer import Customer
    from app.models.opportunity import Opportunity


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
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

    users: Mapped[list["User"]] = relationship("User", back_populates="organization")

    # CRM entity relationships
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="organization")
    customers: Mapped[list["Customer"]] = relationship("Customer", back_populates="organization")
    opportunities: Mapped[list["Opportunity"]] = relationship("Opportunity", back_populates="organization")
