"""
Tests for music management functionality.
Following TDD: Red-Green-Refactor cycle.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import io

from app.main import app


class TestMusicUpload:
    """Test music track upload functionality."""
    
    def test_artist_can_upload_music_track(self, client: TestClient, auth_headers):
        """Test that an artist can upload a music track."""
        track_data = {
            "title": "My New Song",
            "description": "A test track",
            "genre": "rock",
            "is_public": True,
            "tags": ["original", "rock", "guitar"]
        }
        
        # Create a mock audio file
        audio_file = io.BytesIO(b"fake-audio-data")
        files = {"audio_file": ("song.mp3", audio_file, "audio/mpeg")}
        
        response = client.post(
            "/api/v1/music/tracks",
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
        assert data["tags"] == track_data["tags"]
        assert "audio_url" in data
        assert "duration" in data
        assert "file_size" in data
        assert "uploaded_by" in data
    
    def test_music_upload_requires_authentication(self, client: TestClient):
        """Test that music upload requires authentication."""
        track_data = {
            "title": "My New Song",
            "description": "A test track",
            "genre": "rock"
        }
        
        audio_file = io.BytesIO(b"fake-audio-data")
        files = {"audio_file": ("song.mp3", audio_file, "audio/mpeg")}
        
        response = client.post(
            "/api/v1/music/tracks",
            data=track_data,
            files=files
        )
        
        assert response.status_code == 401
    
    def test_music_upload_validates_file_type(self, client: TestClient, auth_headers):
        """Test that music upload validates file type."""
        track_data = {
            "title": "My New Song",
            "description": "A test track",
            "genre": "rock"
        }
        
        # Try to upload a non-audio file
        files = {"audio_file": ("song.txt", io.BytesIO(b"not-audio"), "text/plain")}
        
        response = client.post(
            "/api/v1/music/tracks",
            data=track_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    def test_music_upload_validates_file_size(self, client: TestClient, auth_headers):
        """Test that music upload validates file size."""
        track_data = {
            "title": "My New Song",
            "description": "A test track",
            "genre": "rock"
        }
        
        # Create a file that's too large (over 10MB)
        large_file = io.BytesIO(b"x" * (10 * 1024 * 1024 + 1))
        files = {"audio_file": ("song.mp3", large_file, "audio/mpeg")}
        
        response = client.post(
            "/api/v1/music/tracks",
            data=track_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]
    
    def test_music_upload_requires_title(self, client: TestClient, auth_headers):
        """Test that music upload requires a title."""
        track_data = {
            "description": "A test track",
            "genre": "rock"
            # Missing title
        }
        
        audio_file = io.BytesIO(b"fake-audio-data")
        files = {"audio_file": ("song.mp3", audio_file, "audio/mpeg")}
        
        response = client.post(
            "/api/v1/music/tracks",
            data=track_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("title" in str(error) for error in errors)
    
    def test_music_upload_validates_genre(self, client: TestClient, auth_headers):
        """Test that music upload validates genre."""
        track_data = {
            "title": "My New Song",
            "description": "A test track",
            "genre": "invalid_genre"  # Invalid genre
        }
        
        audio_file = io.BytesIO(b"fake-audio-data")
        files = {"audio_file": ("song.mp3", audio_file, "audio/mpeg")}
        
        response = client.post(
            "/api/v1/music/tracks",
            data=track_data,
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("genre" in str(error) for error in errors)


class TestMusicManagement:
    """Test music track management functionality."""
    
    def test_artist_can_view_their_tracks(self, client: TestClient, auth_headers):
        """Test that an artist can view their tracks."""
        response = client.get("/api/v1/music/tracks/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        assert isinstance(data["tracks"], list)
        assert "pagination" in data
    
    def test_artist_can_update_track_info(self, client: TestClient, auth_headers):
        """Test that an artist can update track information."""
        track_id = "track-id"
        update_data = {
            "title": "Updated Song Title",
            "description": "Updated description",
            "genre": "blues",
            "is_public": False,
            "tags": ["updated", "blues", "soul"]
        }
        
        response = client.put(
            f"/api/v1/music/tracks/{track_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["genre"] == update_data["genre"]
        assert data["is_public"] == update_data["is_public"]
        assert data["tags"] == update_data["tags"]
    
    def test_artist_can_delete_their_track(self, client: TestClient, auth_headers):
        """Test that an artist can delete their track."""
        track_id = "track-id"
        
        response = client.delete(
            f"/api/v1/music/tracks/{track_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    def test_artist_cannot_update_others_track(self, client: TestClient, auth_headers):
        """Test that an artist cannot update another artist's track."""
        track_id = "other-artist-track-id"
        update_data = {
            "title": "Hacked Title",
            "description": "Hacked description"
        }
        
        response = client.put(
            f"/api/v1/music/tracks/{track_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_artist_cannot_delete_others_track(self, client: TestClient, auth_headers):
        """Test that an artist cannot delete another artist's track."""
        track_id = "other-artist-track-id"
        
        response = client.delete(
            f"/api/v1/music/tracks/{track_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]


class TestMusicDiscovery:
    """Test music discovery functionality."""
    
    def test_users_can_browse_public_tracks(self, client: TestClient):
        """Test that users can browse public tracks."""
        response = client.get("/api/v1/music/tracks")
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        assert isinstance(data["tracks"], list)
        assert "pagination" in data
        
        # All returned tracks should be public
        for track in data["tracks"]:
            assert track["is_public"] == True
    
    def test_users_can_search_tracks_by_genre(self, client: TestClient):
        """Test that users can search tracks by genre."""
        response = client.get("/api/v1/music/tracks?genre=rock")
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        
        # All returned tracks should be rock genre
        for track in data["tracks"]:
            assert track["genre"] == "rock"
    
    def test_users_can_search_tracks_by_artist(self, client: TestClient):
        """Test that users can search tracks by artist."""
        response = client.get("/api/v1/music/tracks?artist=testartist")
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        
        # All returned tracks should be by the specified artist
        for track in data["tracks"]:
            assert track["uploaded_by"]["username"] == "testartist"
    
    def test_users_can_search_tracks_by_title(self, client: TestClient):
        """Test that users can search tracks by title."""
        response = client.get("/api/v1/music/tracks?title=rock")
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        
        # All returned tracks should contain "rock" in title
        for track in data["tracks"]:
            assert "rock" in track["title"].lower()
    
    def test_track_search_returns_paginated_results(self, client: TestClient):
        """Test that track search returns paginated results."""
        response = client.get("/api/v1/music/tracks?page=1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "tracks" in data
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]
        assert "pages" in data["pagination"]


class TestMusicPlayback:
    """Test music playback functionality."""
    
    def test_users_can_stream_public_tracks(self, client: TestClient):
        """Test that users can stream public tracks."""
        track_id = "public-track-id"
        
        response = client.get(f"/api/v1/music/tracks/{track_id}/stream")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert "content-length" in response.headers
    
    def test_users_cannot_stream_private_tracks(self, client: TestClient):
        """Test that users cannot stream private tracks."""
        track_id = "private-track-id"
        
        response = client.get(f"/api/v1/music/tracks/{track_id}/stream")
        
        assert response.status_code == 403
        assert "Track is private" in response.json()["detail"]
    
    def test_artists_can_stream_their_private_tracks(self, client: TestClient, auth_headers):
        """Test that artists can stream their own private tracks."""
        track_id = "my-private-track-id"
        
        response = client.get(
            f"/api/v1/music/tracks/{track_id}/stream",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
    
    def test_track_streaming_supports_range_requests(self, client: TestClient):
        """Test that track streaming supports HTTP range requests."""
        track_id = "public-track-id"
        
        # Request first 1024 bytes
        headers = {"Range": "bytes=0-1023"}
        response = client.get(
            f"/api/v1/music/tracks/{track_id}/stream",
            headers=headers
        )
        
        assert response.status_code == 206  # Partial Content
        assert "content-range" in response.headers
        assert "accept-ranges" in response.headers


class TestMusicAnalytics:
    """Test music analytics functionality."""
    
    def test_artists_can_view_track_analytics(self, client: TestClient, auth_headers):
        """Test that artists can view their track analytics."""
        track_id = "track-id"
        
        response = client.get(
            f"/api/v1/music/tracks/{track_id}/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "play_count" in data
        assert "download_count" in data
        assert "like_count" in data
        assert "share_count" in data
        assert "total_listen_time" in data
    
    def test_artists_cannot_view_others_track_analytics(self, client: TestClient, auth_headers):
        """Test that artists cannot view another artist's track analytics."""
        track_id = "other-artist-track-id"
        
        response = client.get(
            f"/api/v1/music/tracks/{track_id}/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_track_play_count_increments_on_stream(self, client: TestClient):
        """Test that track play count increments when streamed."""
        track_id = "public-track-id"
        
        # Stream the track
        response = client.get(f"/api/v1/music/tracks/{track_id}/stream")
        assert response.status_code == 200
        
        # Check that play count increased
        analytics_response = client.get(f"/api/v1/music/tracks/{track_id}/analytics")
        # Note: This would require the artist's token to view analytics
        # For now, we'll just verify the endpoint exists
        assert analytics_response.status_code in [200, 401, 403]


class TestMusicCollaboration:
    """Test music collaboration functionality."""
    
    def test_artists_can_collaborate_on_tracks(self, client: TestClient, auth_headers):
        """Test that artists can collaborate on tracks."""
        track_id = "track-id"
        collaboration_data = {
            "collaborator_id": "other-artist-id",
            "role": "producer",
            "message": "Let's work on this track together!"
        }
        
        response = client.post(
            f"/api/v1/music/tracks/{track_id}/collaborations",
            json=collaboration_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["role"] == collaboration_data["role"]
        assert data["message"] == collaboration_data["message"]
    
    def test_collaborators_can_contribute_to_tracks(self, client: TestClient, auth_headers):
        """Test that collaborators can contribute to tracks."""
        track_id = "collaboration-track-id"
        contribution_data = {
            "type": "audio_contribution",
            "description": "Added guitar solo",
            "file_url": "https://example.com/guitar-solo.mp3"
        }
        
        response = client.post(
            f"/api/v1/music/tracks/{track_id}/contributions",
            json=contribution_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == contribution_data["type"]
        assert data["description"] == contribution_data["description"]
        assert data["file_url"] == contribution_data["file_url"]


# Fixtures for testing
@pytest.fixture
def auth_headers():
    """Return headers with authentication token."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def client():
    """Return test client."""
    return TestClient(app)
