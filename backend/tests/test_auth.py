"""
Tests for authentication functionality.
Following TDD: Red-Green-Refactor cycle.
Uses real database with cleanup.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserRole


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_user_can_register_with_valid_data(self, client: TestClient):
        """Test that a user can register with valid data."""
        user_data = {
            "email": "testuser@example.com",
            "username": "testuser123",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }
        
        try:
            response = client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["user"]["email"] == user_data["email"]
            assert data["user"]["username"] == user_data["username"]
            assert data["user"]["display_name"] == user_data["display_name"]
            assert data["user"]["role"] == user_data["role"]
            assert "access_token" in data
            assert "refresh_token" in data
            
        finally:
            # Clean up: Delete the test user
            self._cleanup_test_user(user_data["email"])
    
    def test_artist_can_register_with_artist_role(self, client: TestClient):
        """Test that an artist can register with artist role through the general auth endpoint."""
        artist_data = {
            "email": "testartistrole@example.com",
            "username": "testartistrole123",
            "password": "securepassword123",
            "display_name": "Test Artist",
            "role": "artist"
        }
        
        try:
            response = client.post("/api/v1/auth/register", json=artist_data)
            assert response.status_code == 201
            data = response.json()
            assert data["user"]["role"] == "artist"
            assert "access_token" in data
            assert "refresh_token" in data
        finally:
            # Clean up test user
            self._cleanup_test_user("testartistrole@example.com")
    
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
            "email": "passwordtest@example.com",  # Unique email
            "username": "passwordtest",
            "password": "weak",  # Too short
            "display_name": "Password Test",
            "role": "user"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # 422 is correct for validation errors
        errors = response.json()["detail"]
        assert "Password" in str(errors)  # Error message is capitalized
    
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
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "securepassword123",
            "display_name": "User 1",
            "role": "user"
        }
        
        try:
            # First registration should succeed
            response1 = client.post("/api/v1/auth/register", json=user_data)
            assert response1.status_code == 201
            
            # Second registration with same email should fail
            user_data["username"] = "user2"  # Different username
            response2 = client.post("/api/v1/auth/register", json=user_data)
            assert response2.status_code == 400
            assert "Email already registered" in response2.json()["detail"]  # Fixed capitalization
            
        finally:
            # Clean up: Delete the test user
            self._cleanup_test_user(user_data["email"])
    
    def test_registration_prevents_duplicate_username(self, client: TestClient):
        """Test that registration prevents duplicate usernames."""
        user_data1 = {
            "email": "user1@example.com",
            "username": "duplicate_username",
            "password": "securepassword123",
            "display_name": "User 1",
            "role": "user"
        }
        
        user_data2 = {
            "email": "user2@example.com",
            "username": "duplicate_username",  # Same username
            "password": "securepassword123",
            "display_name": "User 2",
            "role": "user"
        }
        
        try:
            # First registration should succeed
            response1 = client.post("/api/v1/auth/register", json=user_data1)
            assert response1.status_code == 201
            
            # Second registration with same username should fail
            response2 = client.post("/api/v1/auth/register", json=user_data2)
            assert response2.status_code == 400
            assert "Username already taken" in response2.json()["detail"]  # Fixed capitalization
            
        finally:
            # Clean up: Delete the test users
            self._cleanup_test_user(user_data1["email"])
            self._cleanup_test_user(user_data2["email"])
    
    def _cleanup_test_user(self, email: str):
        """Clean up test user from database."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                db.delete(user)
                db.commit()
        except Exception as e:
            print(f"Warning: Could not clean up test user {email}: {e}")
        finally:
            db.close()


class TestUserLogin:
    """Test user login functionality."""
    
    def test_user_can_login_with_valid_credentials(self, client: TestClient):
        """Test that a user can login with valid credentials."""
        # First register a user
        user_data = {
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "securepassword123",
            "display_name": "Login User",
            "role": "user"
        }
        
        try:
            client.post("/api/v1/auth/register", json=user_data)
            
            # Then try to login
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            
        finally:
            # Clean up
            self._cleanup_test_user(user_data["email"])
    
    def test_login_fails_with_invalid_password(self, client: TestClient):
        """Test that login fails with invalid password."""
        # First register a user
        user_data = {
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "securepassword123",
            "display_name": "Login User",
            "role": "user"
        }
        
        try:
            client.post("/api/v1/auth/register", json=user_data)
            
            # Then try to login with wrong password
            login_data = {
                "username": user_data["username"],
                "password": "wrongpassword"
            }
            
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 401
            assert "Incorrect username or password" in response.json()["detail"]
            
        finally:
            # Clean up
            self._cleanup_test_user(user_data["email"])
    
    def test_login_fails_with_nonexistent_user(self, client: TestClient):
        """Test that login fails with nonexistent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def _cleanup_test_user(self, email: str):
        """Clean up test user from database."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                db.delete(user)
                db.commit()
        except Exception as e:
            print(f"Warning: Could not clean up test user {email}: {e}")
        finally:
            db.close()


class TestTokenManagement:
    """Test JWT token management."""
    
    def test_access_token_contains_user_info(self, client: TestClient):
        """Test that access token contains user information."""
        # Register and login to get a token
        user_data = {
            "email": "tokenuser@example.com",
            "username": "tokenuser",
            "password": "securepassword123",
            "display_name": "Token User",
            "role": "user"
        }
        
        try:
            client.post("/api/v1/auth/register", json=user_data)
            
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            login_response = client.post("/api/v1/auth/login", json=login_data)
            access_token = login_response.json()["access_token"]
            
            # Use token to access protected endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["username"] == user_data["username"]
            assert data["role"] == user_data["role"]
            
        finally:
            # Clean up
            self._cleanup_test_user(user_data["email"])
    
    def test_invalid_token_returns_unauthorized(self, client: TestClient):
        """Test that invalid token returns unauthorized."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_missing_token_returns_unauthorized(self, client: TestClient):
        """Test that missing token returns unauthorized."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def _cleanup_test_user(self, email: str):
        """Clean up test user from database."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                db.delete(user)
                db.commit()
        except Exception as e:
            print(f"Warning: Could not clean up test user {email}: {e}")
        finally:
            db.close()


class TestUserLogout:
    """Test user logout functionality."""
    
    def test_user_can_logout(self, client: TestClient):
        """Test that a user can logout."""
        # First register and login to get a token
        user_data = {
            "email": "logoutuser@example.com",
            "username": "logoutuser",
            "password": "securepassword123",
            "display_name": "Logout User",
            "role": "user"
        }
        
        try:
            client.post("/api/v1/auth/register", json=user_data)
            
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            login_response = client.post("/api/v1/auth/login", json=login_data)
            access_token = login_response.json()["access_token"]
            
            # Then logout
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/api/v1/auth/logout", headers=headers)
            
            assert response.status_code == 200
            assert "Successfully logged out" in response.json()["message"]
            
        finally:
            # Clean up
            self._cleanup_test_user(user_data["email"])
    
    def test_logout_returns_success_message(self, client: TestClient):
        """Test that logout returns a success message."""
        # First register and login to get a token
        user_data = {
            "email": "logoutuser@example.com",
            "username": "logoutuser",
            "password": "securepassword123",
            "display_name": "Logout User",
            "role": "user"
        }
        
        try:
            client.post("/api/v1/auth/register", json=user_data)
            
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            login_response = client.post("/api/v1/auth/login", json=login_data)
            access_token = login_response.json()["access_token"]
            
            # Logout
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/api/v1/auth/logout", headers=headers)
            
            assert response.status_code == 200
            assert "Successfully logged out" in response.json()["message"]
            
            # Note: In the current simple implementation, tokens are not actually invalidated
            # This would require a token blacklist system which is beyond the current scope
            
        finally:
            # Clean up
            self._cleanup_test_user(user_data["email"])
    
    def _cleanup_test_user(self, email: str):
        """Clean up test user from database."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                db.delete(user)
                db.commit()
        except Exception as e:
            print(f"Warning: Could not clean up test user {email}: {e}")
        finally:
            db.close()


# Fixtures for testing
@pytest.fixture
def client():
    """Return test client."""
    return TestClient(app)
