"""Customer API endpoints."""
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import joinedload

from app.core.dependencies import CurrentUser
from app.db.database import AsyncSession, get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)

router = APIRouter(prefix="/customers", tags=["customers"])


def check_customer_access(customer: Customer, user: User) -> None:
    """Check if user has access to this customer. Raises 404 if not."""
    if user.role == "sales":
        if customer.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Customer not found")
    else:
        # Admin and Manager can access any customer in their organization
        if customer.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Customer not found")


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


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    """Create a new customer."""
    # Validate and set owner
    owner_id = await validate_owner(
        db, customer_data.owner_id, current_user.organization_id, current_user
    )

    # Create customer
    customer = Customer(
        organization_id=current_user.organization_id,
        owner_id=owner_id,
        name=customer_data.name,
        customer_type=customer_data.customer_type,
        email=customer_data.email.lower() if customer_data.email else None,
        phone=customer_data.phone,
        notes=customer_data.notes,
    )

    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    return customer


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    search: str | None = Query(None, max_length=100),
    customer_type: Literal["individual", "company"] | None = None,
    owner_id: UUID | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List customers with optional filters."""
    # Build base query with organization scoping
    base_filter = [Customer.organization_id == current_user.organization_id]

    # Sales users can only see their own customers
    if current_user.role == "sales":
        base_filter.append(Customer.owner_id == current_user.id)
    elif owner_id:
        # Admin/Manager can filter by owner, but only within their org
        base_filter.append(Customer.owner_id == owner_id)

    # Apply filters
    if customer_type:
        base_filter.append(Customer.customer_type == customer_type)

    # Search filter
    search_filter = []
    if search:
        search_term = f"%{search.lower()}%"
        search_filter.append(
            or_(
                func.lower(Customer.name).ilike(search_term),
                func.lower(Customer.email).ilike(search_term),
                func.lower(Customer.phone).ilike(search_term),
            )
        )

    # Count total
    count_stmt = select(func.count(Customer.id)).where(and_(*base_filter, *search_filter))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Fetch customers
    stmt = (
        select(Customer)
        .options(joinedload(Customer.owner))
        .where(and_(*base_filter, *search_filter))
        .order_by(Customer.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    customers = result.unique().scalars().all()

    return {
        "items": customers,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    """Get a specific customer by ID."""
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    check_customer_access(customer, current_user)

    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    """Update a customer."""
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    check_customer_access(customer, current_user)

    # Update fields
    update_data = customer_data.model_dump(exclude_unset=True)

    # Handle owner_id changes for admin/manager
    if "owner_id" in update_data:
        owner_id = update_data.pop("owner_id")
        if owner_id is not None:
            # Validate new owner
            if current_user.role == "sales":
                raise HTTPException(status_code=403, detail="Cannot reassign customers")
            update_data["owner_id"] = await validate_owner(
                db, owner_id, current_user.organization_id, current_user
            )
        else:
            update_data["owner_id"] = owner_id

    # Handle email normalization
    if "email" in update_data and update_data["email"]:
        update_data["email"] = update_data["email"].lower()

    for field, value in update_data.items():
        setattr(customer, field, value)

    customer.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(customer)

    return customer
