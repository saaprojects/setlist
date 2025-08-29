"""
Test suite for authentication functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.models.user import User
from app.models.artist import ArtistProfile, Collaboration
from app.models.music import MusicTrack


class TestUserRegistration:
    """Test user registration functionality."""
    
    @classmethod
    def setup_class(cls):
        """Set up test data and cleanup."""
        # Get database session
        db = next(get_db())
        try:
            # Clean up any existing test users
            cls._cleanup_test_users(db)
        finally:
            db.close()
    
    @classmethod
    def _cleanup_test_users(cls, db: Session):
        """Clean up test users from the database."""
        # Use safe cleanup system from conftest.py
        from conftest import cleanup_test_users
        cleanup_test_users(db)

    def test_user_can_register_with_basic_info(self, client: TestClient):
        """Test that a user can register with basic information."""
        from conftest import create_test_user_id, track_test_user
        
        test_id = create_test_user_id()
        user_data = {
            "email": f"testuser_{test_id}@test.example.com",
            "username": f"testuser_{test_id}",
            "password": "securepassword123",
            "display_name": "Test User",
            "role": "user"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["role"] == "user"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["artist_profile"] is None  # Regular users don't get artist profiles
        
        # Track the created user for safe cleanup
        from app.core.database import get_db
        db = next(get_db())
        try:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if user:
                track_test_user(user.id)
        finally:
            db.close()

    def test_artist_can_register_with_artist_role(self, client: TestClient):
        """Test that an artist can register with artist role through the general auth endpoint."""
        from conftest import create_test_user_id, track_test_user
        
        test_id = create_test_user_id()
        artist_data = {
            "email": f"testartistrole_{test_id}@test.example.com",
            "username": f"testartistrole_{test_id}",
            "password": "securepassword123",
            "display_name": "Test Artist",
            "role": "artist"
        }

        response = client.post("/api/v1/auth/register", json=artist_data)
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["role"] == "artist"
        assert data["artist_profile"] is not None  # Artists get artist profiles automatically
        assert "access_token" in data
        assert "refresh_token" in data
        
        # Track the created user for safe cleanup
        from app.core.database import get_db
        db = next(get_db())
        try:
            user = db.query(User).filter(User.email == artist_data["email"]).first()
            if user:
                track_test_user(user.id)
        finally:
            db.close()

    def test_user_registration_requires_all_fields(self, client: TestClient):
        """Test that user registration requires all mandatory fields."""
        incomplete_data = {
            "email": "incomplete@example.com",
            "username": "incomplete"
            # Missing password and display_name
        }

        response = client.post("/api/v1/auth/register", json=incomplete_data)
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("Field required" in str(error) for error in errors)

    def test_user_registration_validates_password_strength(self, client: TestClient):
        """Test that user registration validates password strength."""
        from conftest import create_test_user_id
        
        test_id = create_test_user_id()
        weak_password_data = {
            "email": f"passwordtest_{test_id}@test.example.com",
            "username": f"passwordtest_{test_id}",
            "password": "123",  # Too short
            "display_name": "Password Test",
            "role": "user"
        }

        response = client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert "Password" in errors

    def test_user_registration_prevents_duplicate_email(self, client: TestClient):
        """Test that user registration prevents duplicate emails."""
        from conftest import create_test_user_id, track_test_user
        
        test_id = create_test_user_id()
        user_data = {
            "email": f"duplicateemail_{test_id}@test.example.com",
            "username": f"duplicateemail_{test_id}",
            "password": "securepassword123",
            "display_name": "Duplicate Email Test",
            "role": "user"
        }

        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same email should fail
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
        
        # Track the created user for safe cleanup
        from app.core.database import get_db
        db = next(get_db())
        try:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if user:
                track_test_user(user.id)
        finally:
            db.close()

    def test_user_registration_prevents_duplicate_username(self, client: TestClient):
        """Test that user registration prevents duplicate usernames."""
        from conftest import create_test_user_id, track_test_user
        
        test_id = create_test_user_id()
        user_data1 = {
            "email": f"duplicateuser1_{test_id}@test.example.com",
            "username": f"duplicateuser1_{test_id}",
            "password": "securepassword123",
            "display_name": "Duplicate User Test 1",
            "role": "user"
        }
        
        user_data2 = {
            "email": f"duplicateuser2_{test_id}@test.example.com",
            "username": f"duplicateuser1_{test_id}",  # Same username
            "password": "securepassword123",
            "display_name": "Duplicate User Test 2",
            "role": "user"
        }

        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data1)
        assert response1.status_code == 201

        # Second registration with same username should fail
        response2 = client.post("/api/v1/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "Username already taken" in response2.json()["detail"]
        
        # Track the created user for safe cleanup
        from app.core.database import get_db
        db = next(get_db())
        try:
            user = db.query(User).filter(User.email == user_data1["email"]).first()
            if user:
                track_test_user(user.id)
        finally:
            db.close()


class TestUserLogin:
    """Test user login functionality."""
    
    @classmethod
    def setup_class(cls):
        """Set up test data and cleanup."""
        # Get database session
        db = next(get_db())
        try:
            # Clean up any existing test users
            cls._cleanup_test_users(db)
        finally:
            db.close()
    
    @classmethod
    def _cleanup_test_users(cls, db: Session):
        """Clean up test users from the database."""
        # Delete test users (identified by @example.com emails)
        test_users = db.query(User).filter(User.email.like("%@example.com")).all()
        for user in test_users:
            # Delete related records first (in correct order)
            # Delete collaborations where user is requester or target
            collaborations = db.query(Collaboration).filter(
                (Collaboration.requester_id == user.id) | (Collaboration.target_artist_id == user.id)
            ).all()
            for collab in collaborations:
                db.delete(collab)
            
            # Delete music tracks by user
            music_tracks = db.query(MusicTrack).filter(MusicTrack.artist_id == user.id).all()
            for track in music_tracks:
                db.delete(track)
            
            # Delete associated artist profile if it exists
            artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
            if artist_profile:
                db.delete(artist_profile)
            
            # Finally delete the user
            db.delete(user)
        
        db.commit()
        
        # Reset sequences
        db.execute(text("SELECT setval('users_id_seq', 1, false)"))
        db.execute(text("SELECT setval('artist_profiles_id_seq', 1, false)"))
        db.execute(text("SELECT setval('music_tracks_id_seq', 1, false)"))
        db.execute(text("SELECT setval('collaborations_id_seq', 1, false)"))
        db.commit()

    def test_user_can_login_with_valid_credentials(self, client: TestClient):
        """Test that a user can login with valid credentials."""
        # First register a user
        user_data = {
            "email": "logintest@example.com",
            "username": "logintest",
            "password": "securepassword123",
            "display_name": "Login Test User",
            "role": "user"
        }

        try:
            # Register user
            register_response = client.post("/api/v1/auth/register", json=user_data)
            assert register_response.status_code == 201

            # Login with valid credentials
            login_data = {
                "username": "logintest",
                "password": "securepassword123"
            }
            
            response = client.post("/api/v1/auth/login", data=login_data)
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["username"] == "logintest"
        finally:
            # Clean up test user
            db = next(get_db())
            try:
                self._cleanup_test_users(db)
            finally:
                db.close()

    def test_user_cannot_login_with_invalid_credentials(self, client: TestClient):
        """Test that a user cannot login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestUserAuthentication:
    """Test user authentication and authorization."""
    
    @classmethod
    def setup_class(cls):
        """Set up test data and cleanup."""
        # Get database session
        db = next(get_db())
        try:
            # Clean up any existing test users
            cls._cleanup_test_users(db)
        finally:
            db.close()
    
    @classmethod
    def _cleanup_test_users(cls, db: Session):
        """Clean up test users from the database."""
        # Delete test users (identified by @example.com emails)
        test_users = db.query(User).filter(User.email.like("%@example.com")).all()
        for user in test_users:
            # Delete related records first (in correct order)
            # Delete collaborations where user is requester or target
            collaborations = db.query(Collaboration).filter(
                (Collaboration.requester_id == user.id) | (Collaboration.target_artist_id == user.id)
            ).all()
            for collab in collaborations:
                db.delete(collab)
            
            # Delete music tracks by user
            music_tracks = db.query(MusicTrack).filter(MusicTrack.artist_id == user.id).all()
            for track in music_tracks:
                db.delete(track)
            
            # Delete associated artist profile if it exists
            artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
            if artist_profile:
                db.delete(artist_profile)
            
            # Finally delete the user
            db.delete(user)
        
        db.commit()
        
        # Reset sequences
        db.execute(text("SELECT setval('users_id_seq', 1, false)"))
        db.execute(text("SELECT setval('artist_profiles_id_seq', 1, false)"))
        db.execute(text("SELECT setval('music_tracks_id_seq', 1, false)"))
        db.execute(text("SELECT setval('collaborations_id_seq', 1, false)"))
        db.commit()

    def test_user_can_access_protected_endpoint_with_valid_token(self, client: TestClient):
        """Test that a user can access protected endpoints with a valid token."""
        # First register a user
        user_data = {
            "email": "authtest@example.com",
            "username": "authtest",
            "password": "securepassword123",
            "display_name": "Auth Test User",
            "role": "user"
        }

        try:
            # Register user
            register_response = client.post("/api/v1/auth/register", json=user_data)
            assert register_response.status_code == 201
            access_token = register_response.json()["access_token"]

            # Access protected endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "authtest"
        finally:
            # Clean up test user
            db = next(get_db())
            try:
                self._cleanup_test_users(db)
            finally:
                db.close()

    def test_user_cannot_access_protected_endpoint_without_token(self, client: TestClient):
        """Test that a user cannot access protected endpoints without a token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_user_cannot_access_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test that a user cannot access protected endpoints with an invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
