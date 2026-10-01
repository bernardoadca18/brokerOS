"""
Tests for authentication endpoints and functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
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
        # Check session cookie is set
        cookies = response.cookies
        assert "session" in cookies
        # Verify cookie properties
        cookie_header = response.headers.get("set-cookie", "")
        assert "HttpOnly" in cookie_header or "httponly" in cookie_header.lower()
        assert "Path=/" in cookie_header or "path=/" in cookie_header.lower()

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

    @pytest.mark.asyncio
    async def test_login_inactive_organization(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
    ):
        """Test that users from inactive organizations cannot login."""
        from app.core.security import get_password_hash

        # Create inactive organization
        inactive_org = Organization(
            name="Inactive Org",
            slug="inactive-org",
            is_active=False,
        )
        test_session.add(inactive_org)
        await test_session.commit()
        await test_session.refresh(inactive_org)

        # Create active user in inactive organization
        user = User(
            organization_id=inactive_org.id,
            full_name="User In Inactive Org",
            email="user@inactive.org",
            password_hash=get_password_hash("TestPassword123!"),
            role="admin",
            is_active=True,
        )
        test_session.add(user)
        await test_session.commit()

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": "inactive-org",
                "email": "user@inactive.org",
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401
        # Should not reveal the organization exists
        assert "Invalid credentials" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_error_messages_generic(
        self,
        client: AsyncClient,
        test_admin: User,
        test_org,
    ):
        """Test that all login failures return generic 'Invalid credentials' message."""
        # Unknown organization
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": "unknown-org",
                "email": "any@email.com",
                "password": "AnyPassword123!",
            },
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

        # Known organization, unknown user
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": "unknown@test.com",
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

        # Known organization, known user, wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org.slug,
                "email": test_admin.email,
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestLogout:
    """Tests for the logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(self, authenticated_admin_client: AsyncClient):
        """Test successful logout clears the cookie."""
        response = await authenticated_admin_client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logout successful"
        # Verify session cookie is cleared
        cookies = response.cookies
        # After logout, the session cookie should be empty/expired
        assert "session" not in cookies or cookies.get("session") == ""

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, client: AsyncClient):
        """Test logout works even without authentication."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logout successful"


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
    async def test_same_password_different_hashes(self, test_session, test_org):
        """Test that same password produces different hashes due to salts."""
        from app.core.security import get_password_hash, verify_password

        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # Different salts produce different hashes
        assert hash1 != hash2
        # Both hashes verify the same password
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    @pytest.mark.asyncio
    async def test_password_verification(self, test_session, test_org):
        """Test that password verification works correctly."""
        from app.core.security import get_password_hash, verify_password

        password = "TestPassword123!"
        password_hash = get_password_hash(password)
        # Correct password verifies
        assert verify_password(password, password_hash)
        # Wrong password does not verify
        assert not verify_password("WrongPassword123!", password_hash)
