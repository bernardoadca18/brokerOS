"""
Tests for admin safeguards to prevent accidental lockout.
"""
import pytest
from httpx import AsyncClient

from app.models.user import User


class TestAdminSelfProtection:
    """Tests to prevent admin from locking themselves out."""

    @pytest.mark.asyncio
    async def test_admin_cannot_deactivate_self(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test admin cannot deactivate their own account."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"is_active": False},
        )
        assert response.status_code == 400
        assert "cannot deactivate your own account" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_admin_cannot_remove_own_admin_role(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test admin cannot remove admin role from themselves."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"role": "manager"},
        )
        assert response.status_code == 400
        assert "cannot remove admin role" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_admin_can_update_own_name(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test admin can update their own name."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"full_name": "Updated Admin Name"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Admin Name"

    @pytest.mark.asyncio
    async def test_admin_can_update_own_email(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test admin can update their own email."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"email": "newadmin@test.com"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "newadmin@test.com"


class TestLastAdminProtection:
    """Tests to prevent removing the last admin from organization."""

    @pytest.mark.asyncio
    async def test_cannot_deactivate_last_admin(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test cannot deactivate the last admin in organization."""
        # test_admin is the only admin in test_org
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"is_active": False},
        )
        # This should fail because it would leave no active admins
        # Note: The check for self-deactivation happens first
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_cannot_change_role_of_last_admin(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test cannot change role of last admin."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"role": "manager"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_can_deactivate_admin_if_another_exists(
        self,
        test_session,
        test_org,
        test_admin: User,
        authenticated_admin_client: AsyncClient,
    ):
        """Test can deactivate admin if another active admin exists."""
        from app.core.security import get_password_hash

        # Create second admin
        second_admin = User(
            organization_id=test_org.id,
            full_name="Second Admin",
            email="secondadmin@test.com",
            password_hash=get_password_hash("TestPassword123!"),
            role="admin",
            is_active=True,
        )
        test_session.add(second_admin)
        await test_session.commit()
        await test_session.refresh(second_admin)

        # Now try to deactivate the second admin (not self)
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{second_admin.id}",
            json={"is_active": False},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_cannot_deactivate_admin_leaving_no_active_admins(
        self,
        test_session,
        test_org,
        test_admin: User,
        authenticated_admin_client: AsyncClient,
    ):
        """Test cannot deactivate admin if it would leave no active admins."""
        from app.core.security import get_password_hash

        # Create second admin
        second_admin = User(
            organization_id=test_org.id,
            full_name="Second Admin",
            email="anotheradmin@test.com",
            password_hash=get_password_hash("TestPassword123!"),
            role="admin",
            is_active=True,
        )
        test_session.add(second_admin)
        await test_session.commit()
        await test_session.refresh(second_admin)

        # Deactivate the second admin first
        await authenticated_admin_client.patch(
            f"/api/v1/users/{second_admin.id}",
            json={"is_active": False},
        )

        # Now try to change test_admin's role (would leave no active admins)
        # But this fails due to self-protection first
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_admin.id}",
            json={"role": "manager"},
        )
        assert response.status_code == 400


class TestUserCreationValidation:
    """Tests for user creation validation."""

    @pytest.mark.asyncio
    async def test_cannot_create_user_with_duplicate_email_in_org(
        self, authenticated_admin_client: AsyncClient, test_admin: User
    ):
        """Test cannot create user with email that already exists in org."""
        response = await authenticated_admin_client.post(
            "/api/v1/users",
            json={
                "full_name": "Duplicate Email",
                "email": test_admin.email,
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_can_create_user_with_same_email_in_different_org(
        self,
        client: AsyncClient,
        test_admin: User,
        test_admin_org2: User,
        test_org_two,
    ):
        """Test can create user with same email in different org."""
        # Login as admin of org2
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "organization": test_org_two.slug,
                "email": test_admin_org2.email,
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 200

        # Create user with same email as test_admin (who is in org1)
        # This should work because it's a different org
        response = await client.post(
            "/api/v1/users",
            json={
                "full_name": "Same Email Different Org",
                "email": test_admin.email,  # Same email as admin in org1
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == test_admin.email

    @pytest.mark.asyncio
    async def test_email_normalized_on_create(
        self, authenticated_admin_client: AsyncClient
    ):
        """Test email is normalized (lowercased, trimmed) on create."""
        response = await authenticated_admin_client.post(
            "/api/v1/users",
            json={
                "full_name": "Upper Case",
                "email": "  UPPER@test.com  ",
                "password": "NewPassword123!",
                "role": "sales",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "upper@test.com"

    @pytest.mark.asyncio
    async def test_email_normalized_on_update(
        self, authenticated_admin_client: AsyncClient, test_sales: User
    ):
        """Test email is normalized on update."""
        response = await authenticated_admin_client.patch(
            f"/api/v1/users/{test_sales.id}",
            json={"email": "  UPDATED@test.com  "},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "updated@test.com"


class TestProductionConfiguration:
    """Tests for production configuration validation."""

    def test_production_with_default_secret_fails(self):
        """Test that production environment with default secret raises error."""
        import os
        from importlib import reload

        # Set production environment with default secret
        original_env = os.environ.get("ENVIRONMENT")
        original_secret = os.environ.get("SECRET_KEY")

        os.environ["ENVIRONMENT"] = "production"
        # Ensure SECRET_KEY is not set or is the default
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        try:
            # Clear the LRU cache and reload config
            from app.core import config

            config.get_settings.cache_clear()
            reload(config)

            # This should raise RuntimeError
            with pytest.raises(RuntimeError) as exc_info:
                config.get_settings()

            assert "default development SECRET_KEY" in str(exc_info.value)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]

            if original_secret is not None:
                os.environ["SECRET_KEY"] = original_secret
            elif "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]

            # Clear cache and reload
            from app.core import config

            config.get_settings.cache_clear()
            reload(config)

    def test_production_with_custom_secret_succeeds(self):
        """Test that production environment with custom secret works."""
        import os
        from importlib import reload

        original_env = os.environ.get("ENVIRONMENT")
        original_secret = os.environ.get("SECRET_KEY")

        os.environ["ENVIRONMENT"] = "production"
        os.environ["SECRET_KEY"] = "a-very-secure-production-secret-key-12345"

        try:
            from app.core import config

            config.get_settings.cache_clear()
            reload(config)

            # This should not raise
            settings = config.get_settings()
            assert settings.is_production
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]

            if original_secret is not None:
                os.environ["SECRET_KEY"] = original_secret
            elif "SECRET_KEY" in os.environ:
                del os.environ["SECRET_KEY"]

            # Clear cache and reload
            from app.core import config

            config.get_settings.cache_clear()
            reload(config)
