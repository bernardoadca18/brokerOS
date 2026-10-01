from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "ok",
        "service": "brokeros-api",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "0.1.0",
    }
