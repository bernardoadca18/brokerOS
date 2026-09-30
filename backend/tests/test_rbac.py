"""
Tests for Role-Based Access Control (RBAC).
"""
import pytest
from httpx import AsyncClient

from app.models.user import User


class TestAdminRole:
    """Tests for admin role permissions."""

    @pytest.mark.asyncio
    async def test_admin_can_list_users(self, authenticated_admin_client: AsyncClient):
        """Test admin can list all users in organization."""
        response = await authenticated_admin_client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_admin_can_create_user(
        self, authenticated_admin_client: AsyncClient, test_org
    ):
        """Test admin can create new users."""
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
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "sales"

    @pytest.mark.asyncio
    async def test_admin_can_update_user(
        self, authenticated_admin_client: AsyncClient, test_sales: User
    ):
        """Test admin can update user details."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_sales.id}",
            json={"full_name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_admin_can_deactivate_user(
        self, authenticated_admin_client: AsyncClient, test_sales: User
    ):
        """Test admin can deactivate users."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_sales.id}",
            json={"is_active": False},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_admin_can_change_user_role(
        self, authenticated_admin_client: AsyncClient, test_sales: User
    ):
        """Test admin can change user roles."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_sales.id}",
            json={"role": "manager"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "manager"

    @pytest.mark.asyncio
    async def test_admin_can_get_organization(self, authenticated_admin_client: AsyncClient):
        """Test admin can view organization details."""
        response = await authenticated_admin_client.get("/api/v1/organization")
        assert response.status_code == 200


class TestManagerRole:
    """Tests for manager role permissions."""

    @pytest.mark.asyncio
    async def test_manager_can_list_users(self, authenticated_manager_client: AsyncClient):
        """Test manager can list users."""
        response = await authenticated_manager_client.get("/api/v1/users")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_manager_can_get_user(
        self, authenticated_manager_client: AsyncClient, test_sales: User
    ):
        """Test manager can view user details."""
        response = await authenticated_manager_client.get(f"/api/v1/users/{test_sales.id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_manager_cannot_create_user(
        self, authenticated_manager_client: AsyncClient
    ):
        """Test manager cannot create users."""
        response = await authenticated_manager_client.post(
            "/api/v1/users",
            json={
                "full_name": "New User",
                "email": "newuser@test.com",
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_manager_cannot_update_user(
        self, authenticated_manager_client: AsyncClient, test_sales: User
    ):
        """Test manager cannot update users."""
        response = await authenticated_manager_client.patch(
            f"/api/v1/users/{test_sales.id}",
            json={"full_name": "Updated Name"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_manager_can_get_organization(self, authenticated_manager_client: AsyncClient):
        """Test manager can view organization details."""
        response = await authenticated_manager_client.get("/api/v1/organization")
        assert response.status_code == 200


class TestSalesRole:
    """Tests for sales role permissions."""

    @pytest.mark.asyncio
    async def test_sales_cannot_list_users(self, authenticated_sales_client: AsyncClient):
        """Test sales cannot list users."""
        response = await authenticated_sales_client.get("/api/v1/users")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_sales_cannot_create_user(self, authenticated_sales_client: AsyncClient):
        """Test sales cannot create users."""
        response = await authenticated_sales_client.post(
            "/api/v1/users",
            json={
                "full_name": "New User",
                "email": "newuser@test.com",
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_sales_can_get_organization(self, authenticated_sales_client: AsyncClient):
        """Test sales can view organization details."""
        response = await authenticated_sales_client.get("/api/v1/organization")
        assert response.status_code == 200


class TestUnauthenticatedAccess:
    """Tests for unauthenticated access."""

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_list_users(self, client: AsyncClient):
        """Test unauthenticated users cannot list users."""
        response = await client.get("/api/v1/users")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_create_user(self, client: AsyncClient):
        """Test unauthenticated users cannot create users."""
        response = await client.post(
            "/api/v1/users",
            json={
                "full_name": "New User",
                "email": "newuser@test.com",
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_unauthenticated_can_access_health(self, client: AsyncClient):
        """Test unauthenticated users can access health endpoint."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
