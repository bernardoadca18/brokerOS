"""
Test configuration and fixtures for BrokerOS backend tests.
"""
import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test environment variables before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENVIRONMENT"] = "development"

from app.core.security import get_password_hash
from app.db.database import Base, get_db
from app.main import app
from app.models.organization import Organization
from app.models.user import User

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test user credentials
TEST_PASSWORD = "TestPassword123!"
TEST_PASSWORD_HASH = get_password_hash(TEST_PASSWORD)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    # Import aiosqlite for SQLite support

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_org(test_session: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        slug="test-org",
        is_active=True,
    )
    test_session.add(org)
    await test_session.commit()
    await test_session.refresh(org)
    return org


@pytest_asyncio.fixture(scope="function")
async def test_org_two(test_session: AsyncSession) -> Organization:
    """Create a second test organization for tenant isolation tests."""
    org = Organization(
        name="Second Organization",
        slug="second-org",
        is_active=True,
    )
    test_session.add(org)
    await test_session.commit()
    await test_session.refresh(org)
    return org


@pytest_asyncio.fixture(scope="function")
async def test_admin(test_session: AsyncSession, test_org: Organization) -> User:
    """Create a test admin user."""
    admin = User(
        organization_id=test_org.id,
        full_name="Admin User",
        email="admin@test.com",
        password_hash=TEST_PASSWORD_HASH,
        role="admin",
        is_active=True,
    )
    test_session.add(admin)
    await test_session.commit()
    await test_session.refresh(admin)
    return admin


@pytest_asyncio.fixture(scope="function")
async def test_manager(test_session: AsyncSession, test_org: Organization) -> User:
    """Create a test manager user."""
    manager = User(
        organization_id=test_org.id,
        full_name="Manager User",
        email="manager@test.com",
        password_hash=TEST_PASSWORD_HASH,
        role="manager",
        is_active=True,
    )
    test_session.add(manager)
    await test_session.commit()
    await test_session.refresh(manager)
    return manager


@pytest_asyncio.fixture(scope="function")
async def test_sales(test_session: AsyncSession, test_org: Organization) -> User:
    """Create a test sales user."""
    sales = User(
        organization_id=test_org.id,
        full_name="Sales User",
        email="sales@test.com",
        password_hash=TEST_PASSWORD_HASH,
        role="sales",
        is_active=True,
    )
    test_session.add(sales)
    await test_session.commit()
    await test_session.refresh(sales)
    return sales


@pytest_asyncio.fixture(scope="function")
async def test_admin_org2(
    test_session: AsyncSession, test_org_two: Organization
) -> User:
    """Create a test admin user in a different organization."""
    admin = User(
        organization_id=test_org_two.id,
        full_name="Admin Org2",
        email="admin@org2.com",
        password_hash=TEST_PASSWORD_HASH,
        role="admin",
        is_active=True,
    )
    test_session.add(admin)
    await test_session.commit()
    await test_session.refresh(admin)
    return admin


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authenticated_admin_client(
    client: AsyncClient, test_admin: User, test_org: Organization
) -> AsyncClient:
    """Create an authenticated client as admin."""
    # Login to get the cookie
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "organization": test_org.slug,
            "email": test_admin.email,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 200
    return client


@pytest_asyncio.fixture(scope="function")
async def authenticated_manager_client(
    client: AsyncClient, test_manager: User, test_org: Organization
) -> AsyncClient:
    """Create an authenticated client as manager."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "organization": test_org.slug,
            "email": test_manager.email,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 200
    return client


@pytest_asyncio.fixture(scope="function")
async def authenticated_sales_client(
    client: AsyncClient, test_sales: User, test_org: Organization
) -> AsyncClient:
    """Create an authenticated client as sales."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "organization": test_org.slug,
            "email": test_sales.email,
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 200
    return client
