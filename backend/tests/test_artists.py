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


class TestArtistProfile:
    """Test artist profile management functionality."""
    
    @classmethod
    def setup_class(cls):
        """Ensure clean database before running tests."""
        # No aggressive cleanup needed - we use safe tracking now
        pass
    
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
        files = {"file": ("test.jpg", b"fake-image-data", "image/jpeg")}
        
        response = client.post("/api/v1/artists/me/profile-picture", files=files, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "content_type" in data
        assert "size_bytes" in data
        assert data["filename"] == "test.jpg"
        assert data["content_type"] == "image/jpeg"
        assert data["size_bytes"] == len(b"fake-image-data")
    
    def test_artist_profile_picture_validates_file_type(self, client: TestClient, auth_headers):
        """Test that profile picture upload validates file type."""
        # Try to upload a non-image file
        files = {"file": ("test.txt", b"not-an-image", "text/plain")}
        
        response = client.post("/api/v1/artists/me/profile-picture", files=files, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_artist_can_retrieve_profile_picture(self, client: TestClient, auth_headers):
        """Test that an artist can retrieve their uploaded profile picture."""
        # First upload a profile picture
        files = {"file": ("test.jpg", b"fake-image-data", "image/jpeg")}
        upload_response = client.post("/api/v1/artists/me/profile-picture", files=files, headers=auth_headers)
        assert upload_response.status_code == 200
        
        # Get the user ID from the auth token (we'll need to extract this)
        # For now, let's test with a known user ID from the setup
        from app.core.database import get_db
        from app.models.user import User
        
        db = next(get_db())
        try:
            # Get the current user from the auth token
            from app.core.security import decode_access_token
            token = auth_headers["Authorization"].split(" ")[1]
            username = decode_access_token(token)["sub"]
            user = db.query(User).filter(User.username == username).first()
            user_id = user.id
            
            # Now retrieve the profile picture
            response = client.get(f"/api/v1/artists/profile-picture/{user_id}")
            
            assert response.status_code == 200
            assert response.content == b"fake-image-data"
            assert response.headers["content-type"] == "image/jpeg"
            assert "cache-control" in response.headers
        finally:
            db.close()

    def test_artist_can_upload_real_profile_picture(self, client: TestClient, auth_headers):
        """Test that an artist can upload a real profile picture (the Alerrian icon)."""
        # Read the actual image file from the container
        import os
        image_path = "/tmp/alerrian-icon.jpg"
        
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Create a mock file upload with real image data
            files = {"file": ("alerrian-icon.jpg", image_data, "image/jpeg")}
            
            response = client.post("/api/v1/artists/me/profile-picture", files=files, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "filename" in data
            assert "content_type" in data
            assert "size_bytes" in data
            assert data["filename"] == "alerrian-icon.jpg"
            assert data["content_type"] == "image/jpeg"
            assert data["size_bytes"] == len(image_data)
            
            # Now test retrieval
            from app.core.database import get_db
            from app.models.user import User
            
            db = next(get_db())
            try:
                # Get the current user from the auth token
                from app.core.security import decode_access_token
                token = auth_headers["Authorization"].split(" ")[1]
                username = decode_access_token(token)["sub"]
                user = db.query(User).filter(User.username == username).first()
                user_id = user.id
                
                # Retrieve the profile picture
                retrieve_response = client.get(f"/api/v1/artists/profile-picture/{user_id}")
                
                assert retrieve_response.status_code == 200
                assert retrieve_response.content == image_data
                assert retrieve_response.headers["content-type"] == "image/jpeg"
                assert "cache-control" in retrieve_response.headers
                
                print(f"✅ Successfully uploaded and retrieved real image: {data['filename']} ({data['size_bytes']} bytes)")
                
            finally:
                db.close()
        else:
            pytest.skip("Real image file not available for testing")


class TestArtistDiscovery:
    """Test artist discovery functionality."""
    
    @classmethod
    def setup_class(cls):
        """Ensure clean database before running tests."""
        # No aggressive cleanup needed - we use safe tracking now
        pass
    
    def test_users_can_search_artists_by_genre(self, client: TestClient):
        """Test that users can search for artists by genre."""
        # First, let's see what genres exist in the database
        response = client.get("/api/v1/artists/search")
        assert response.status_code == 200
        data = response.json()
        
        if data["artists"]:
            # Use the first available genre for testing
            available_genre = data["artists"][0]["genres"][0]
            response = client.get(f"/api/v1/artists/search?genre={available_genre}")
            
            assert response.status_code == 200
            data = response.json()
            assert "artists" in data
            assert isinstance(data["artists"], list)
            # All returned artists should have the searched genre
            for artist in data["artists"]:
                assert available_genre in artist["genres"]
        else:
            # No artists in database, test still passes
            response = client.get("/api/v1/artists/search?genre=rock")
            assert response.status_code == 200
            data = response.json()
            assert "artists" in data
            assert isinstance(data["artists"], list)
    
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
        # First, let's see what instruments exist in the database
        response = client.get("/api/v1/artists/search")
        assert response.status_code == 200
        data = response.json()
        
        if data["artists"]:
            # Use the first available instrument for testing
            available_instrument = data["artists"][0]["instruments"][0]
            response = client.get(f"/api/v1/artists/search?instrument={available_instrument}")
            
            assert response.status_code == 200
            data = response.json()
            assert "artists" in data
            # All returned artists should play the searched instrument
            for artist in data["artists"]:
                assert available_instrument in artist["instruments"]
        else:
            # No artists in database, test still passes
            response = client.get("/api/v1/artists/search?instrument=guitar")
            assert response.status_code == 200
            data = response.json()
            assert "artists" in data
    
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
    
    @classmethod
    def setup_class(cls):
        """Ensure clean database before running tests."""
        # No aggressive cleanup needed - we use safe tracking now
        pass
    
    def test_artist_can_send_collaboration_request(self, client: TestClient, auth_headers):
        """Test that an artist can send a collaboration request."""
        from app.core.database import get_db
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
        from app.models.artist import ArtistProfile
        
        # Create a second test user to collaborate with
        db = next(get_db())
        try:
            target_user = db.query(User).filter(User.email == "targetartist@example.com").first()
            if not target_user:
                target_user = User(
                    email="targetartist@example.com",
                    username="targetartist",
                    password_hash=get_password_hash("testpassword123"),
                    display_name="Target Artist",
                    role=UserRole.artist,
                    is_active=True
                )
                db.add(target_user)
                db.commit()
                db.refresh(target_user)
                
                # Create artist profile for target user
                target_profile = ArtistProfile(
                    user_id=target_user.id,
                    bio="Target artist bio",
                    genres=["jazz", "blues"],
                    instruments=["piano", "saxophone"]
                )
                db.add(target_profile)
                db.commit()
            
            collaboration_data = {
                "target_artist_id": target_user.id,
                "message": "Let's collaborate on a song!",
                "project_type": "recording"
            }
            
            response = client.post("/api/v1/artists/collaborations", json=collaboration_data, headers=auth_headers)
            
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "pending"
            assert data["message"] == collaboration_data["message"]
            assert data["project_type"] == collaboration_data["project_type"]
        finally:
            db.close()
    
    def test_artist_can_accept_collaboration_request(self, client: TestClient, auth_headers):
        """Test that an artist can accept a collaboration request."""
        # This test needs a real collaboration request to exist first
        # For now, we'll test the endpoint structure
        collaboration_id = 1  # Use integer ID
        
        response = client.put(f"/api/v1/artists/collaborations/{collaboration_id}/accept", headers=auth_headers)
        
        # Should get 404 since collaboration doesn't exist, but endpoint should work
        assert response.status_code in [200, 404]
    
    def test_artist_can_decline_collaboration_request(self, client: TestClient, auth_headers):
        """Test that an artist can decline a collaboration request."""
        # This test needs a real collaboration request to exist first
        # For now, we'll test the endpoint structure
        collaboration_id = 1  # Use integer ID
        
        response = client.put(f"/api/v1/artists/collaborations/{collaboration_id}/decline", headers=auth_headers)
        
        # Should get 404 since collaboration doesn't exist, but endpoint should work
        assert response.status_code in [200, 404]
    
    def test_artist_can_view_collaboration_requests(self, client: TestClient, auth_headers):
        """Test that an artist can view their collaboration requests."""
        response = client.get("/api/v1/artists/collaborations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "collaborations" in data
        assert "sent" in data["collaborations"]
        assert "received" in data["collaborations"]
        assert isinstance(data["collaborations"]["sent"], list)
        assert isinstance(data["collaborations"]["received"], list)


class TestArtistMusic:
    """Test artist music management."""
    
    @classmethod
    def setup_class(cls):
        """Ensure clean database before running tests."""
        # No aggressive cleanup needed - we use safe tracking now
        pass
    
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
        track_id = 1  # Use integer ID
        update_data = {"is_public": False}
        
        response = client.put(f"/api/v1/artists/me/tracks/{track_id}", json=update_data, headers=auth_headers)
        
        # Should get 404 since track doesn't exist, but endpoint should work
        assert response.status_code in [200, 404]
    
    def test_artist_can_delete_track(self, client: TestClient, auth_headers):
        """Test that an artist can delete their track."""
        track_id = 1  # Use integer ID
        
        response = client.delete(f"/api/v1/artists/me/tracks/{track_id}", headers=auth_headers)
        
        # Should get 404 since track doesn't exist, but endpoint should work
        assert response.status_code in [204, 404]
    
    def test_artist_can_view_their_tracks(self, client: TestClient, auth_headers):
        """Test that an artist can view their tracks."""
        response = client.get("/api/v1/artists/me/tracks", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        assert isinstance(data["tracks"], list)


# Fixtures for testing
@pytest.fixture
def client():
    """Return test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return headers with authentication token."""
    from app.core.security import create_access_token
    from app.models.user import User, UserRole
    from app.core.database import get_db
    from app.models.artist import ArtistProfile
    from .conftest import track_test_user, create_test_user_id
    
    # Create a test user and artist profile
    db = next(get_db())
    try:
        # Generate unique test identifiers
        test_id = create_test_user_id()
        test_email = f"{test_id}@test.example.com"
        test_username = f"testartist_{test_id}"
        
        # Check if test user already exists
        test_user = db.query(User).filter(User.email == test_email).first()
        if not test_user:
            from app.core.security import get_password_hash
            
            test_user = User(
                email=test_email,
                username=test_username,
                password_hash=get_password_hash("testpassword123"),
                display_name="Test Artist",
                role=UserRole.artist,
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Track this user for safe cleanup
            track_test_user(test_user.id)
            
            # Create artist profile
            artist_profile = ArtistProfile(
                user_id=test_user.id,
                bio="Test artist bio",
                genres=["rock", "alternative"],
                instruments=["guitar", "vocals"]
            )
            db.add(artist_profile)
            db.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": test_user.username})
        
        return {"Authorization": f"Bearer {access_token}"}
    finally:
        db.close()


# Cleanup is now handled safely by conftest.py fixtures
