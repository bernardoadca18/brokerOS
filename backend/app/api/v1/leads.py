"""Lead API endpoints."""
from datetime import UTC, date, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import joinedload

from app.core.dependencies import CurrentUser
from app.db.database import AsyncSession, get_db
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.lead import (
    LeadConversionRequest,
    LeadConversionResponse,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)

router = APIRouter(prefix="/leads", tags=["leads"])


def check_lead_access(lead: Lead, user: User) -> None:
    """Check if user has access to this lead. Raises 404 if not."""
    if user.role == "sales":
        if lead.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Lead not found")
    else:
        # Admin and Manager can access any lead in their organization
        if lead.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Lead not found")


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


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Lead:
    """Create a new lead."""
    # Validate contact information
    if not lead_data.email and not lead_data.phone:
        raise HTTPException(
            status_code=422,
            detail="At least one contact method (email or phone) is required",
        )

    # Validate and set owner
    owner_id = await validate_owner(
        db, lead_data.owner_id, current_user.organization_id, current_user
    )

    # Create lead
    lead = Lead(
        organization_id=current_user.organization_id,
        owner_id=owner_id,
        full_name=lead_data.full_name,
        email=lead_data.email.lower() if lead_data.email else None,
        phone=lead_data.phone,
        product_interest=lead_data.product_interest,
        source=lead_data.source,
        notes=lead_data.notes,
    )

    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return lead


@router.get("", response_model=LeadListResponse)
async def list_leads(
    search: str | None = Query(None, max_length=100),
    status: Literal["new", "contacted", "qualified", "unqualified", "converted"] | None = None,
    product_interest: Literal["vehicle_insurance", "consortium"] | None = None,
    source: Literal["manual", "website", "referral", "whatsapp", "campaign", "other"] | None = None,
    owner_id: UUID | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List leads with optional filters."""
    # Build base query with organization scoping
    base_filter = [Lead.organization_id == current_user.organization_id]

    # Sales users can only see their own leads
    if current_user.role == "sales":
        base_filter.append(Lead.owner_id == current_user.id)
    elif owner_id:
        # Admin/Manager can filter by owner, but only within their org
        base_filter.append(Lead.owner_id == owner_id)

    # Apply filters
    if status:
        base_filter.append(Lead.status == status)
    if product_interest:
        base_filter.append(Lead.product_interest == product_interest)
    if source:
        base_filter.append(Lead.source == source)

    # Search filter
    search_filter = []
    if search:
        search_term = f"%{search.lower()}%"
        search_filter.append(
            or_(
                func.lower(Lead.full_name).ilike(search_term),
                func.lower(Lead.email).ilike(search_term),
                func.lower(Lead.phone).ilike(search_term),
            )
        )

    # Count total
    count_stmt = select(func.count(Lead.id)).where(and_(*base_filter, *search_filter))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Fetch leads with owner information
    stmt = (
        select(Lead)
        .options(joinedload(Lead.owner))
        .where(and_(*base_filter, *search_filter))
        .order_by(Lead.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    leads = result.unique().scalars().all()

    return {
        "items": leads,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Lead:
    """Get a specific lead by ID."""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    check_lead_access(lead, current_user)

    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Lead:
    """Update a lead."""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    check_lead_access(lead, current_user)

    # Update fields
    update_data = lead_data.model_dump(exclude_unset=True)

    # Handle owner_id changes for admin/manager
    if "owner_id" in update_data:
        owner_id = update_data.pop("owner_id")
        if owner_id is not None:
            # Validate new owner
            if current_user.role == "sales":
                raise HTTPException(status_code=403, detail="Cannot reassign leads")
            update_data["owner_id"] = await validate_owner(
                db, owner_id, current_user.organization_id, current_user
            )
        else:
            update_data["owner_id"] = owner_id

    # Handle email normalization
    if "email" in update_data and update_data["email"]:
        update_data["email"] = update_data["email"].lower()

    for field, value in update_data.items():
        setattr(lead, field, value)

    lead.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(lead)

    return lead


@router.post("/{lead_id}/convert", response_model=LeadConversionResponse)
async def convert_lead(
    lead_id: UUID,
    conversion_data: LeadConversionRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Convert a lead to customer and opportunity atomically."""
    # Fetch the lead
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    check_lead_access(lead, current_user)

    # Check if already converted
    if lead.status == "converted":
        raise HTTPException(
            status_code=409,
            detail="Lead has already been converted",
        )

    # Determine owner - keep the same owner as the lead
    owner_id = lead.owner_id

    # Create Customer
    customer = Customer(
        organization_id=lead.organization_id,
        owner_id=owner_id,
        name=lead.full_name,
        customer_type=conversion_data.customer_type,
        email=lead.email,
        phone=lead.phone,
        notes=conversion_data.notes,
    )
    db.add(customer)
    await db.flush()  # Get customer ID

    # Determine product type
    product_type = conversion_data.product_type or lead.product_interest

    # Create Opportunity
    opportunity_title = conversion_data.opportunity_title or f"{product_type.replace('_', ' ').title()} - {lead.full_name}"

    # Parse expected_close_date if provided
    expected_close_date = None
    if conversion_data.expected_close_date:
        try:
            expected_close_date = date.fromisoformat(conversion_data.expected_close_date)
        except ValueError:
            pass

    opportunity = Opportunity(
        organization_id=lead.organization_id,
        owner_id=owner_id,
        customer_id=customer.id,
        lead_id=lead.id,
        title=opportunity_title,
        product_type=product_type,
        stage="qualification",
        amount=conversion_data.amount,
        expected_close_date=expected_close_date,
        notes=conversion_data.notes,
    )
    db.add(opportunity)

    # Mark lead as converted
    lead.status = "converted"
    lead.updated_at = datetime.now(UTC)

    # Commit all changes atomically
    await db.commit()

    # Refresh to get all relationships
    await db.refresh(lead)
    await db.refresh(customer)
    await db.refresh(opportunity)

    return {
        "lead": lead,
        "customer": customer,
        "opportunity": opportunity,
    }
