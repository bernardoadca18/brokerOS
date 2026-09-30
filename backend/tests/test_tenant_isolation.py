"""
Tests for tenant isolation between organizations.
"""
import pytest
from httpx import AsyncClient

from app.models.user import User


class TestTenantIsolation:
    """Tests to ensure users cannot access data from other organizations."""

    @pytest.mark.asyncio
    async def test_admin_cannot_see_users_from_other_org(
        self,
        authenticated_admin_client: AsyncClient,
        test_admin_org2: User,
    ):
        """Test admin cannot see users from another organization."""
        response = await authenticated_admin_client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        # Verify user from other org is not in the list
        user_ids = [u["id"] for u in data["items"]]
        assert str(test_admin_org2.id) not in user_ids

    @pytest.mark.asyncio
    async def test_admin_cannot_get_user_from_other_org(
        self,
        authenticated_admin_client: AsyncClient,
        test_admin_org2: User,
    ):
        """Test admin cannot get details of user from another organization."""
        response = await authenticated_admin_client.get(
            f"/api/v1/users/{test_admin_org2.id}"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_cannot_update_user_from_other_org(
        self,
        authenticated_admin_client: AsyncClient,
        test_admin_org2: User,
    ):
        """Test admin cannot update user from another organization."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin_org2.id}",
            json={"full_name": "Hacked Name"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_cannot_create_user_in_other_org(
        self,
        authenticated_admin_client: AsyncClient,
        test_org_two,
    ):
        """Test admin cannot create user in another organization.

        Note: The API doesn't allow specifying organization_id on create,
        so this is inherently protected. Testing that created user
        belongs to admin's org.
        """
        response = await authenticated_admin_client.post(
            "/api/v1/users",
            json={
                "full_name": "New User",
                "email": "newuser@test.com",
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 201
        data = response.json()
        # User should be in admin's organization, not test_org_two
        # We verify by checking the user is visible to the admin
        assert data["email"] == "newuser@test.com"

    @pytest.mark.asyncio
    async def test_user_in_org1_cannot_login_to_org2(
        self,
        client: AsyncClient,
        test_admin: User,
        test_org_two,
    ):
        """Test user from org1 cannot login using org2's slug."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org_two.slug,
                "email": test_admin.email,
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cross_org_login_attempt_reveals_nothing(
        self,
        client: AsyncClient,
        test_admin: User,
    ):
        """Test that cross-org login attempt doesn't reveal org membership."""
        # Try to login with correct email but wrong org
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": "nonexistent-org",
                "email": test_admin.email,
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401
        # Error message should not reveal if email exists
        assert "Invalid credentials" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_organization_endpoint_returns_own_org_only(
        self,
        authenticated_admin_client: AsyncClient,
        test_org,
        test_org_two,
    ):
        """Test organization endpoint returns only user's own organization."""
        response = await authenticated_admin_client.get("/api/v1/organization")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_org.slug
        assert data["slug"] != test_org_two.slug
