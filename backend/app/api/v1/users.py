import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import AdminUser, ManagerUser, require_role
from app.core.security import get_password_hash, verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Any:
    """List users in the current user's organization. Admin and Manager only."""
    # Count total users in organization
    count_result = await db.execute(
        select(func.count()).where(User.organization_id == current_user.organization_id)
    )
    total = count_result.scalar() or 0

    # Get users in organization
    result = await db.execute(
        select(User)
        .where(User.organization_id == current_user.organization_id)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    current_user: AdminUser,
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Create a new user. Admin only."""
    # Normalize email
    normalized_email = user_data.email.lower().strip()

    # Check if email already exists in organization
    existing_result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.email == normalized_email,
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists in the organization",
        )

    # Create user
    user = User(
        organization_id=current_user.organization_id,
        full_name=user_data.full_name,
        email=normalized_email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Get a specific user. Admin and Manager only."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    current_user: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Update a user. Admin only."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from deactivating themselves
    if user.id == current_user.id and user_data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    # Prevent admin from removing their own admin role
    if (
        user.id == current_user.id
        and user.role == "admin"
        and user_data.role is not None
        and user_data.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove admin role from your own account",
        )

    # Prevent deactivating the last admin
    if user.role == "admin" and user_data.is_active is False:
        # Count other active admins
        admin_count_result = await db.execute(
            select(func.count()).where(
                User.organization_id == current_user.organization_id,
                User.role == "admin",
                User.is_active == True,
                User.id != user_id,
            )
        )
        other_active_admins = admin_count_result.scalar() or 0
        if other_active_admins == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last admin in the organization",
            )

    # Prevent removing admin role from the last admin
    if (
        user.role == "admin"
        and user_data.role is not None
        and user_data.role != "admin"
    ):
        admin_count_result = await db.execute(
            select(func.count()).where(
                User.organization_id == current_user.organization_id,
                User.role == "admin",
                User.is_active == True,
                User.id != user_id,
            )
        )
        other_active_admins = admin_count_result.scalar() or 0
        if other_active_admins == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove admin role from the last admin in the organization",
            )

    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.email is not None:
        normalized_email = user_data.email.lower().strip()
        # Check if email already exists in organization
        existing_result = await db.execute(
            select(User).where(
                User.organization_id == current_user.organization_id,
                User.email == normalized_email,
                User.id != user_id,
            )
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists in the organization",
            )
        user.email = normalized_email
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)
