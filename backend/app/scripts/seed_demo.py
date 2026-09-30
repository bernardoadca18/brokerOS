"""Seed script to create demo organization and users for development."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.database import async_session_maker
from app.models.organization import Organization
from app.models.user import User

DEMO_ORG_NAME = "BrokerOS Demo"
DEMO_ORG_SLUG = "demo"
DEMO_PASSWORD = "demo123456"  # noqa: S105

DEMO_USERS = [
    {
        "full_name": "Admin User",
        "email": "admin@brokeros.local",
        "role": "admin",
    },
    {
        "full_name": "Manager User",
        "email": "manager@brokeros.local",
        "role": "manager",
    },
    {
        "full_name": "Sales User",
        "email": "sales@brokeros.local",
        "role": "sales",
    },
]


async def seed_demo() -> None:
    """Create demo organization and users if they don't exist."""
    async with async_session_maker() as session:
        # Check if demo organization exists
        result = await session.execute(
            select(Organization).where(Organization.slug == DEMO_ORG_SLUG)
        )
        org = result.scalar_one_or_none()

        if not org:
            # Create demo organization
            org = Organization(
                name=DEMO_ORG_NAME,
                slug=DEMO_ORG_SLUG,
                is_active=True,
            )
            session.add(org)
            await session.flush()
            print(f"Created organization: {DEMO_ORG_NAME} ({DEMO_ORG_SLUG})")
        else:
            print(f"Organization already exists: {org.name} ({org.slug})")

        # Create demo users
        for user_data in DEMO_USERS:
            normalized_email = user_data["email"].lower().strip()
            user_result = await session.execute(
                select(User).where(
                    User.organization_id == org.id,
                    User.email == normalized_email,
                )
            )
            existing_user: User | None = user_result.scalar_one_or_none()

            if not existing_user:
                new_user = User(
                    organization_id=org.id,
                    full_name=user_data["full_name"],
                    email=normalized_email,
                    password_hash=get_password_hash(DEMO_PASSWORD),
                    role=user_data["role"],
                    is_active=True,
                )
                session.add(new_user)
                await session.flush()
                print(
                    f"Created user: {user_data['full_name']} ({user_data['role']}) - {user_data['email']}"
                )
            else:
                print(f"User already exists: {existing_user.full_name} ({existing_user.email})")

        await session.commit()
        print("\n=== Demo Credentials ===")
        print(f"Organization: {DEMO_ORG_SLUG}")
        for user_data in DEMO_USERS:
            print(f"  {user_data['role']}: {user_data['email']} / {DEMO_PASSWORD}")
        print("========================\n")


if __name__ == "__main__":
    print("Seeding demo data...\n")
    asyncio.run(seed_demo())
