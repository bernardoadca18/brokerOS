from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import CurrentUser
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.user import UserWithOrganizationResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


class LoginRequest(BaseModel):
    organization: str
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user: UserWithOrganizationResponse


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Authenticate user and set session cookie."""
    # Find organization by slug
    org_result = await db.execute(
        select(Organization).where(Organization.slug == request.organization)
    )
    organization = org_result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Find user by email (normalized to lowercase)
    normalized_email = request.email.lower().strip()
    user_result = await db.execute(
        select(User).where(
            User.organization_id == organization.id,
            User.email == normalized_email,
        )
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set HTTP-only cookie
    response.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )

    return LoginResponse(
        message="Login successful",
        user=UserWithOrganizationResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """Clear session cookie."""
    response.delete_cookie(key="session", path="/")
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserWithOrganizationResponse)
async def get_current_user_info(current_user: CurrentUser) -> Any:
    """Get current authenticated user information."""
    return UserWithOrganizationResponse.model_validate(current_user)
