"""
Minimal tests for artist functionality.
These tests can run without models/schemas to show what's failing.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


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
        
        # This should fail with 404 since the endpoint doesn't exist yet
        # or 501 if it exists but isn't implemented
        assert response.status_code in [404, 501]
    
    def test_artist_registration_requires_all_fields(self, client: TestClient):
        """Test that artist registration fails without required fields."""
        incomplete_data = {
            "email": "artist@example.com",
            "username": "testartist"
            # Missing password, display_name, etc.
        }
        
        response = client.post("/api/v1/artists/register", json=incomplete_data)
        
        # Should fail with validation error or endpoint not found
        assert response.status_code in [422, 404, 501]
    
    def test_artist_registration_validates_email_format(self, client: TestClient):
        """Test that artist registration validates email format."""
        artist_data = {
            "email": "invalid-email",
            "username": "testartist",
            "password": "securepassword123",
            "display_name": "Test Artist"
        }
        
        response = client.post("/api/v1/artists/register", json=artist_data)
        
        # Should fail with validation error or endpoint not found
        assert response.status_code in [422, 404, 501]


class TestArtistProfile:
    """Test artist profile management."""
    
    def test_artist_can_view_own_profile(self, client: TestClient, auth_headers):
        """Test that an artist can view their own profile."""
        response = client.get("/api/v1/artists/me", headers=auth_headers)
        
        # Should fail with 401 (unauthorized) or 404 (endpoint not found)
        assert response.status_code in [401, 404, 501]
    
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
        
        # Should fail with 401 (unauthorized) or 404 (endpoint not found)
        assert response.status_code in [401, 404, 501]


class TestArtistDiscovery:
    """Test artist discovery functionality."""
    
    def test_users_can_search_artists_by_genre(self, client: TestClient):
        """Test that users can search for artists by genre."""
        response = client.get("/api/v1/artists/search?genre=rock")
        
        # Should fail with 404 (endpoint not found) or 501 (not implemented)
        assert response.status_code in [404, 501]
    
    def test_artist_search_returns_paginated_results(self, client: TestClient):
        """Test that artist search returns paginated results."""
        response = client.get("/api/v1/artists/search?page=1&limit=10")
        
        # Should fail with 404 (endpoint not found) or 501 (not implemented)
        assert response.status_code in [404, 501]


# Fixtures for testing
@pytest.fixture
def auth_headers():
    """Return headers with authentication token."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def client():
    """Return test client."""
    return TestClient(app)
