from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "ok",
        "service": "brokeros-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }
