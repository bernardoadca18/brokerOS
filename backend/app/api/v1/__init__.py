from fastapi import APIRouter

from app.api.v1 import auth, health, organizations, users, leads, customers, opportunities

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organizations.router)
api_router.include_router(leads.router)
api_router.include_router(customers.router)
api_router.include_router(opportunities.router)
