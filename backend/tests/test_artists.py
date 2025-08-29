"""
Tests for artist functionality.
Following TDD: Red-Green-Refactor cycle.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.artist import ArtistProfile
from app.schemas.artist import ArtistCreate, ArtistUpdate, ArtistResponse


class TestArtistRegistration:
    """Test artist registration functionality."""
    
    def test_artist_can_register_with_basic_info(self, client: TestClient):
        """Test that an artist can register with basic information."""
        artist_data = {
            "email": "artist@example.com",
            "username": "testartist",
            "password": "securepassword123",
            "display_name": "Test Artist",
            "bio": "I'm a test artist",
            "genres": ["rock", "alternative"],
            "instruments": ["guitar", "vocals"]
        }
        
        response = client.post("/api/v1/artists/register", json=artist_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == artist_data["email"]
        assert data["user"]["username"] == artist_data["username"]
        assert data["user"]["display_name"] == artist_data["display_name"]
        assert data["user"]["role"] == "artist"
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_artist_registration_requires_all_fields(self, client: TestClient):
        """Test that artist registration fails without required fields."""
        incomplete_data = {
            "email": "artist@example.com",
            "username": "testartist"
            # Missing password, display_name, etc.
        }
        
        response = client.post("/api/v1/artists/register", json=incomplete_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("password" in str(error) for error in errors)
        assert any("display_name" in str(error) for error in errors)
    
    def test_artist_registration_validates_email_format(self, client: TestClient):
        """Test that artist registration validates email format."""
        artist_data = {
            "email": "invalid-email",
            "username": "testartist",
            "password": "securepassword123",
            "display_name": "Test Artist"
        }
        
        response = client.post("/api/v1/artists/register", json=artist_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("email" in str(error) for error in errors)
    
    def test_artist_registration_validates_password_strength(self, client: TestClient):
        """Test that artist registration validates password strength."""
        artist_data = {
            "email": "artist@example.com",
            "username": "testartist",
            "password": "weak",  # Too short
            "display_name": "Test Artist"
        }
        
        response = client.post("/api/v1/artists/register", json=artist_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("password" in str(error) for error in errors)
    
    def test_artist_registration_prevents_duplicate_email(self, client: TestClient):
        """Test that artist registration prevents duplicate emails."""
        artist_data = {
            "email": "artist@example.com",
            "username": "testartist",
            "password": "securepassword123",
            "display_name": "Test Artist"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/artists/register", json=artist_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = client.post("/api/v1/artists/register", json=artist_data)
        assert response2.status_code == 400
        assert "email already registered" in response2.json()["detail"]
    
    def test_artist_registration_prevents_duplicate_username(self, client: TestClient):
        """Test that artist registration prevents duplicate usernames."""
        artist_data1 = {
            "email": "artist1@example.com",
            "username": "testartist",
            "password": "securepassword123",
            "display_name": "Test Artist 1"
        }
        
        artist_data2 = {
            "email": "artist2@example.com",
            "username": "testartist",  # Same username
            "password": "securepassword123",
            "display_name": "Test Artist 2"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/artists/register", json=artist_data1)
        assert response1.status_code == 201
        
        # Second registration with same username should fail
        response2 = client.post("/api/v1/artists/register", json=artist_data2)
        assert response2.status_code == 400
        assert "username already taken" in response2.json()["detail"]


class TestArtistProfile:
    """Test artist profile management."""
    
    def test_artist_can_view_own_profile(self, client: TestClient, auth_headers):
        """Test that an artist can view their own profile."""
        response = client.get("/api/v1/artists/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "artist"
        assert "genres" in data
        assert "instruments" in data
        assert "bio" in data
    
    def test_artist_can_update_profile(self, client: TestClient, auth_headers):
        """Test that an artist can update their profile."""
        update_data = {
            "bio": "Updated bio",
            "genres": ["rock", "blues", "jazz"],
            "instruments": ["guitar", "piano"],
            "location": "New York, NY",
            "website": "https://example.com"
        }
        
        response = client.put("/api/v1/artists/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == update_data["bio"]
        assert data["genres"] == update_data["genres"]
        assert data["instruments"] == update_data["instruments"]
        assert data["location"] == update_data["location"]
        assert data["website"] == update_data["website"]
    
    def test_artist_can_upload_profile_picture(self, client: TestClient, auth_headers):
        """Test that an artist can upload a profile picture."""
        # Create a mock image file
        files = {"profile_picture": ("test.jpg", b"fake-image-data", "image/jpeg")}
        
        response = client.post("/api/v1/artists/me/profile-picture", files=files, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "profile_picture_url" in data
        assert data["profile_picture_url"].startswith("http")
    
    def test_artist_profile_picture_validates_file_type(self, client: TestClient, auth_headers):
        """Test that profile picture upload validates file type."""
        # Try to upload a non-image file
        files = {"profile_picture": ("test.txt", b"not-an-image", "text/plain")}
        
        response = client.post("/api/v1/artists/me/profile-picture", files=files, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]


class TestArtistDiscovery:
    """Test artist discovery functionality."""
    
    def test_users_can_search_artists_by_genre(self, client: TestClient):
        """Test that users can search for artists by genre."""
        response = client.get("/api/v1/artists/search?genre=rock")
        
        assert response.status_code == 200
        data = response.json()
        assert "artists" in data
        assert isinstance(data["artists"], list)
        # All returned artists should have "rock" in their genres
        for artist in data["artists"]:
            assert "rock" in artist["genres"]
    
    def test_users_can_search_artists_by_location(self, client: TestClient):
        """Test that users can search for artists by location."""
        response = client.get("/api/v1/artists/search?location=New York")
        
        assert response.status_code == 200
        data = response.json()
        assert "artists" in data
        # All returned artists should be from New York
        for artist in data["artists"]:
            assert "New York" in artist["location"]
    
    def test_users_can_search_artists_by_instrument(self, client: TestClient):
        """Test that users can search for artists by instrument."""
        response = client.get("/api/v1/artists/search?instrument=guitar")
        
        assert response.status_code == 200
        data = response.json()
        assert "artists" in data
        # All returned artists should play guitar
        for artist in data["artists"]:
            assert "guitar" in artist["instruments"]
    
    def test_artist_search_returns_paginated_results(self, client: TestClient):
        """Test that artist search returns paginated results."""
        response = client.get("/api/v1/artists/search?page=1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "artists" in data
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]


class TestArtistCollaboration:
    """Test artist collaboration functionality."""
    
    def test_artist_can_send_collaboration_request(self, client: TestClient, auth_headers):
        """Test that an artist can send a collaboration request."""
        collaboration_data = {
            "target_artist_id": "other-artist-id",
            "message": "Let's collaborate on a song!",
            "project_type": "recording"
        }
        
        response = client.post("/api/v1/artists/collaborations", json=collaboration_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["message"] == collaboration_data["message"]
        assert data["project_type"] == collaboration_data["project_type"]
    
    def test_artist_can_accept_collaboration_request(self, client: TestClient, auth_headers):
        """Test that an artist can accept a collaboration request."""
        collaboration_id = "collab-request-id"
        
        response = client.put(f"/api/v1/artists/collaborations/{collaboration_id}/accept", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
    
    def test_artist_can_decline_collaboration_request(self, client: TestClient, auth_headers):
        """Test that an artist can decline a collaboration request."""
        collaboration_id = "collab-request-id"
        
        response = client.put(f"/api/v1/artists/collaborations/{collaboration_id}/decline", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "declined"
    
    def test_artist_can_view_collaboration_requests(self, client: TestClient, auth_headers):
        """Test that an artist can view their collaboration requests."""
        response = client.get("/api/v1/artists/collaborations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "collaborations" in data
        assert isinstance(data["collaborations"], list)


class TestArtistMusic:
    """Test artist music management."""
    
    def test_artist_can_upload_music_track(self, client: TestClient, auth_headers):
        """Test that an artist can upload a music track."""
        track_data = {
            "title": "My New Song",
            "description": "A test track",
            "genre": "rock",
            "is_public": True
        }
        
        files = {"audio_file": ("song.mp3", b"fake-audio-data", "audio/mpeg")}
        
        response = client.post(
            "/api/v1/artists/me/tracks",
            data=track_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == track_data["title"]
        assert data["description"] == track_data["description"]
        assert data["genre"] == track_data["genre"]
        assert data["is_public"] == track_data["is_public"]
        assert "audio_url" in data
    
    def test_artist_can_make_track_private(self, client: TestClient, auth_headers):
        """Test that an artist can make a track private."""
        track_id = "track-id"
        update_data = {"is_public": False}
        
        response = client.put(f"/api/v1/artists/me/tracks/{track_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] == False
    
    def test_artist_can_delete_track(self, client: TestClient, auth_headers):
        """Test that an artist can delete their track."""
        track_id = "track-id"
        
        response = client.delete(f"/api/v1/artists/me/tracks/{track_id}", headers=auth_headers)
        
        assert response.status_code == 204
    
    def test_artist_can_view_their_tracks(self, client: TestClient, auth_headers):
        """Test that an artist can view their tracks."""
        response = client.get("/api/v1/artists/me/tracks", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        assert isinstance(data["tracks"], list)


# Fixtures for testing
@pytest.fixture
def auth_headers():
    """Return headers with authentication token."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def client():
    """Return test client."""
    return TestClient(app)
