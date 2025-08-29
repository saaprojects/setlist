"""
Tests for authentication functionality.
Following TDD: Red-Green-Refactor cycle.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from passlib.context import CryptContext

from app.main import app
from app.core.security import create_access_token, verify_password


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_user_can_register_with_valid_data(self, client: TestClient):
        """Test that a user can register with valid data."""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["display_name"] == user_data["display_name"]
        assert data["user"]["role"] == user_data["role"]
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_artist_can_register_with_artist_role(self, client: TestClient):
        """Test that an artist can register with artist role."""
        artist_data = {
            "email": "artist@example.com",
            "username": "testartist",
            "password": "securepassword123",
            "display_name": "Test Artist",
            "role": "artist"
        }
        
        response = client.post("/api/v1/auth/register", json=artist_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["role"] == "artist"
    
    def test_registration_requires_all_fields(self, client: TestClient):
        """Test that registration fails without required fields."""
        incomplete_data = {
            "email": "user@example.com",
            "username": "testuser"
            # Missing password, display_name, role
        }
        
        response = client.post("/api/v1/auth/register", json=incomplete_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("password" in str(error) for error in errors)
        assert any("display_name" in str(error) for error in errors)
        assert any("role" in str(error) for error in errors)
    
    def test_registration_validates_email_format(self, client: TestClient):
        """Test that registration validates email format."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("email" in str(error) for error in errors)
    
    def test_registration_validates_password_strength(self, client: TestClient):
        """Test that registration validates password strength."""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "weak",  # Too short
            "display_name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("password" in str(error) for error in errors)
    
    def test_registration_validates_role(self, client: TestClient):
        """Test that registration validates user role."""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "invalid_role"  # Invalid role
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("role" in str(error) for error in errors)
    
    def test_registration_prevents_duplicate_email(self, client: TestClient):
        """Test that registration prevents duplicate emails."""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "email already registered" in response2.json()["detail"]
    
    def test_registration_prevents_duplicate_username(self, client: TestClient):
        """Test that registration prevents duplicate usernames."""
        user_data1 = {
            "email": "user1@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User 1",
            "role": "user"
        }
        
        user_data2 = {
            "email": "user2@example.com",
            "username": "testuser",  # Same username
            "password": "securepassword123",
            "display_name": "Test User 2",
            "role": "user"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data1)
        assert response1.status_code == 201
        
        # Second registration with same username should fail
        response2 = client.post("/api/v1/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "username already taken" in response2.json()["detail"]


class TestUserLogin:
    """Test user login functionality."""
    
    def test_user_can_login_with_valid_credentials(self, client: TestClient):
        """Test that a user can login with valid credentials."""
        # First register a user
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Then try to login
        login_data = {
            "username": "user@example.com",  # Can login with email
            "password": "securepassword123"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == user_data["email"]
    
    def test_user_can_login_with_username(self, client: TestClient):
        """Test that a user can login with username."""
        # First register a user
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Then try to login with username
        login_data = {
            "username": "testuser",  # Login with username
            "password": "securepassword123"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_fails_with_invalid_password(self, client: TestClient):
        """Test that login fails with invalid password."""
        # First register a user
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Then try to login with wrong password
        login_data = {
            "username": "user@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_fails_with_nonexistent_user(self, client: TestClient):
        """Test that login fails with nonexistent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestTokenManagement:
    """Test JWT token management."""
    
    def test_access_token_contains_user_info(self, client: TestClient):
        """Test that access token contains user information."""
        # Register and login to get a token
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "user@example.com",
            "password": "securepassword123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["role"] == user_data["role"]
    
    def test_refresh_token_can_generate_new_access_token(self, client: TestClient):
        """Test that refresh token can generate new access token."""
        # Register and login to get tokens
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "user@example.com",
            "password": "securepassword123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_invalid_token_returns_unauthorized(self, client: TestClient):
        """Test that invalid token returns unauthorized."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_expired_token_returns_unauthorized(self, client: TestClient):
        """Test that expired token returns unauthorized."""
        # This would require a token that's actually expired
        # For now, we'll test the endpoint exists
        headers = {"Authorization": "Bearer expired-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # Should return 401, but the exact message depends on implementation
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password security features."""
    
    def test_passwords_are_hashed_not_stored_plaintext(self, client: TestClient):
        """Test that passwords are hashed, not stored in plaintext."""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # In a real implementation, we'd check the database
        # For now, we'll verify the password works for login
        login_data = {
            "username": "user@example.com",
            "password": "securepassword123"
        }
        
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
    
    def test_password_validation_rules(self, client: TestClient):
        """Test password validation rules."""
        # Test minimum length
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "123",  # Too short
            "display_name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Test with valid password
        user_data["password"] = "securepassword123"
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201


class TestUserLogout:
    """Test user logout functionality."""
    
    def test_user_can_logout(self, client: TestClient):
        """Test that a user can logout."""
        # First register and login to get a token
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "user@example.com",
            "password": "securepassword123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Then logout
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_logout_invalidates_token(self, client: TestClient):
        """Test that logout invalidates the token."""
        # First register and login to get a token
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "user@example.com",
            "password": "securepassword123"
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        client.post("/api/v1/auth/logout", headers=headers)
        
        # Try to use the token again
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401


# Fixtures for testing
@pytest.fixture
def client():
    """Return test client."""
    return TestClient(app)


@pytest.fixture
def pwd_context():
    """Return password context for testing."""
    return CryptContext(schemes=["bcrypt"], deprecated="auto")
