"""Opportunity API endpoints."""
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import joinedload

from app.core.dependencies import CurrentUser
from app.db.database import AsyncSession, get_db
from app.models.customer import Customer
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityUpdate,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def check_opportunity_access(opportunity: Opportunity, user: User) -> None:
    """Check if user has access to this opportunity. Raises 404 if not."""
    if user.role == "sales":
        if opportunity.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Opportunity not found")
    else:
        # Admin and Manager can access any opportunity in their organization
        if opportunity.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Opportunity not found")


async def validate_owner(
    session: AsyncSession, owner_id: UUID | None, organization_id: UUID, user: User
) -> UUID:
    """Validate and return the appropriate owner_id."""
    if user.role == "sales":
        # Sales users always own records they create
        return user.id

    if owner_id is None:
        return user.id

    # Admin/Manager can assign owner, but must be in same org and active
    stmt = select(User).where(
        User.id == owner_id,
        User.organization_id == organization_id,
        User.is_active == True,
    )
    result = await session.execute(stmt)
    owner = result.scalar_one_or_none()

    if not owner:
        raise HTTPException(status_code=404, detail="User not found")

    return owner_id


async def validate_customer(
    session: AsyncSession, customer_id: UUID, user: User
) -> Customer:
    """Validate customer exists and user has access."""
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check tenant isolation
    if customer.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Sales can only use their own customers
    if user.role == "sales" and customer.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Opportunity:
    """Create a new opportunity."""
    # Validate customer access
    customer = await validate_customer(db, opportunity_data.customer_id, current_user)

    # Validate and set owner
    owner_id = await validate_owner(
        db, opportunity_data.owner_id, current_user.organization_id, current_user
    )

    # Create opportunity
    opportunity = Opportunity(
        organization_id=current_user.organization_id,
        owner_id=owner_id,
        customer_id=opportunity_data.customer_id,
        lead_id=opportunity_data.lead_id,
        title=opportunity_data.title,
        product_type=opportunity_data.product_type,
        stage=opportunity_data.stage,
        amount=opportunity_data.amount,
        expected_close_date=opportunity_data.expected_close_date,
        lost_reason=opportunity_data.lost_reason,
        notes=opportunity_data.notes,
    )

    # Handle closed_at for won/lost stages
    if opportunity.stage in ("won", "lost"):
        opportunity.closed_at = datetime.now(UTC)

    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)

    return opportunity


@router.get("", response_model=OpportunityListResponse)
async def list_opportunities(
    search: str | None = Query(None, max_length=100),
    stage: Literal["qualification", "proposal", "negotiation", "won", "lost"] | None = None,
    product_type: Literal["vehicle_insurance", "consortium"] | None = None,
    owner_id: UUID | None = None,
    customer_id: UUID | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List opportunities with optional filters."""
    # Build base query with organization scoping
    base_filter = [Opportunity.organization_id == current_user.organization_id]

    # Sales users can only see their own opportunities
    if current_user.role == "sales":
        base_filter.append(Opportunity.owner_id == current_user.id)
    elif owner_id:
        # Admin/Manager can filter by owner, but only within their org
        base_filter.append(Opportunity.owner_id == owner_id)

    # Apply filters
    if stage:
        base_filter.append(Opportunity.stage == stage)
    if product_type:
        base_filter.append(Opportunity.product_type == product_type)
    if customer_id:
        base_filter.append(Opportunity.customer_id == customer_id)

    # Search filter
    search_filter = []
    if search:
        search_term = f"%{search.lower()}%"
        search_filter.append(
            or_(
                func.lower(Opportunity.title).ilike(search_term),
            )
        )

    # Count total
    count_stmt = select(func.count(Opportunity.id)).where(and_(*base_filter, *search_filter))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Fetch opportunities with customer and owner
    stmt = (
        select(Opportunity)
        .options(joinedload(Opportunity.customer), joinedload(Opportunity.owner))
        .where(and_(*base_filter, *search_filter))
        .order_by(Opportunity.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    opportunities = result.unique().scalars().all()

    return {
        "items": opportunities,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Opportunity:
    """Get a specific opportunity by ID."""
    stmt = (
        select(Opportunity)
        .options(joinedload(Opportunity.customer), joinedload(Opportunity.owner))
        .where(Opportunity.id == opportunity_id)
    )
    result = await db.execute(stmt)
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    check_opportunity_access(opportunity, current_user)

    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: UUID,
    opportunity_data: OpportunityUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Opportunity:
    """Update an opportunity."""
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await db.execute(stmt)
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    check_opportunity_access(opportunity, current_user)

    # Update fields
    update_data = opportunity_data.model_dump(exclude_unset=True)

    # Handle owner_id changes for admin/manager
    if "owner_id" in update_data:
        owner_id = update_data.pop("owner_id")
        if owner_id is not None:
            # Validate new owner
            if current_user.role == "sales":
                raise HTTPException(status_code=403, detail="Cannot reassign opportunities")
            update_data["owner_id"] = await validate_owner(
                db, owner_id, current_user.organization_id, current_user
            )
        else:
            update_data["owner_id"] = owner_id

    # Handle customer_id changes
    if "customer_id" in update_data and update_data["customer_id"]:
        await validate_customer(db, update_data["customer_id"], current_user)

    # Handle stage changes and closed_at
    new_stage = update_data.get("stage", opportunity.stage)
    if new_stage in ("won", "lost") and opportunity.stage not in ("won", "lost"):
        # Moving to closed state
        update_data["closed_at"] = datetime.now(UTC)
    elif new_stage not in ("won", "lost") and opportunity.stage in ("won", "lost"):
        # Reopening from closed state
        update_data["closed_at"] = None
        update_data["lost_reason"] = None

    for field, value in update_data.items():
        setattr(opportunity, field, value)

    opportunity.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(opportunity)

    return opportunity
