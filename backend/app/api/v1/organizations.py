from typing import Any

from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.schemas.organization import OrganizationResponse

router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("", response_model=OrganizationResponse)
async def get_organization(current_user: CurrentUser) -> Any:
    """Get current user's organization."""
    return OrganizationResponse.model_validate(current_user.organization)
