"""
Tests for authentication endpoints and functionality.
"""
import pytest
from httpx import AsyncClient

from app.models.user import User


class TestLogin:
    """Tests for the login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        client: AsyncClient,
        test_admin: User,
        test_org,
    ):
        """Test successful login with valid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": test_admin.email,
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == test_admin.email
        assert data["user"]["role"] == "admin"
        # Check cookie is set
        assert "access_token" in response.cookies or "set-cookie" in response.headers

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_admin: User,
        test_org,
    ):
        """Test login fails with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": test_admin.email,
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_wrong_email(
        self,
        client: AsyncClient,
        test_org,
    ):
        """Test login fails with non-existent email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": "nonexistent@test.com",
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_wrong_organization(
        self,
        client: AsyncClient,
        test_admin: User,
    ):
        """Test login fails with wrong organization slug."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": "wrong-org",
                "email": test_admin.email,
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self,
        client: AsyncClient,
        test_session,
        test_org,
    ):
        """Test login fails for inactive user."""
        # Create inactive user
        from app.core.security import get_password_hash

        inactive_user = User(
            organization_id=test_org.id,
            full_name="Inactive User",
            email="inactive@test.com",
            password_hash=get_password_hash("TestPassword123!"),
            role="sales",
            is_active=False,
        )
        test_session.add(inactive_user)
        await test_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": inactive_user.email,
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_case_insensitive_email(
        self,
        client: AsyncClient,
        test_admin: User,
        test_org,
    ):
        """Test login works with different case email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": test_admin.email.upper(),
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 200


class TestLogout:
    """Tests for the logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(self, authenticated_admin_client: AsyncClient):
        """Test successful logout clears the cookie."""
        response = await authenticated_admin_client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logout successful"

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, client: AsyncClient):
        """Test logout works even without authentication."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200


class TestMeEndpoint:
    """Tests for the /auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_me_authenticated(self, authenticated_admin_client: AsyncClient, test_admin):
        """Test /me returns current user info when authenticated."""
        response = await authenticated_admin_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_admin.email
        assert data["role"] == "admin"
        assert "organization" in data

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client: AsyncClient):
        """Test /me returns 401 when not authenticated."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestPasswordSecurity:
    """Tests for password security features."""

    @pytest.mark.asyncio
    async def test_password_hashed(self, test_admin: User):
        """Test that passwords are stored as hashes, not plaintext."""
        assert test_admin.password_hash != "TestPassword123!"
        assert len(test_admin.password_hash) > 20  # Argon2 hashes are long

    @pytest.mark.asyncio
    async def test_different_passwords_different_hashes(
        self, test_admin: User, test_manager: User
    ):
        """Test that different passwords produce different hashes."""
        assert test_admin.password_hash != test_manager.password_hash

    @pytest.mark.asyncio
    async def test_same_password_different_hashes(self, test_session, test_org):
        """Test that same password produces different hashes (salt)."""
        from app.core.security import get_password_hash

        hash1 = get_password_hash("SamePassword123!")
        hash2 = get_password_hash("SamePassword123!")
        assert hash1 != hash2  # Different salts
