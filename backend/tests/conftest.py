"""
Pytest configuration and fixtures for the Setlist backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('app.core.config.settings') as mock:
        mock.API_V1_STR = "/api/v1"
        mock.PROJECT_NAME = "Setlist"
        mock.BACKEND_HOST = "0.0.0.0"
        mock.BACKEND_PORT = 8000
        mock.BACKEND_RELOAD = True
        mock.BACKEND_LOG_LEVEL = "info"
        mock.ALLOWED_HOSTS = ["http://localhost:3000", "http://localhost:8000"]
        mock.DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"
        mock.SUPABASE_URL = "https://test.supabase.co"
        mock.SUPABASE_API_KEY = "test_key"
        mock.SUPABASE_SECRET_KEY = "test_secret"
        mock.JWT_SECRET_KEY = "test_jwt_secret"
        mock.JWT_ALGORITHM = "HS256"
        mock.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock.MAX_FILE_SIZE = 10485760
        mock.UPLOAD_DIR = "test_uploads/"
        mock.ALLOWED_AUDIO_EXTENSIONS = ["mp3", "wav", "flac", "aac"]
        mock.ALLOWED_VIDEO_EXTENSIONS = ["mp4", "avi", "mov"]
        mock.GOOGLE_CLIENT_ID = "test_google_client_id"
        mock.GOOGLE_CLIENT_SECRET = "test_google_client_secret"
        mock.REDIS_URL = "redis://localhost:6379"
        mock.ENVIRONMENT = "test"
        mock.DEBUG = True
        yield mock


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "display_name": "Test User",
        "role": "user"
    }


@pytest.fixture
def sample_artist_data():
    """Sample artist data for testing."""
    return {
        "email": "artist@example.com",
        "username": "testartist",
        "password": "artistpass123",
        "display_name": "Test Artist",
        "role": "artist",
        "band_name": "Test Band",
        "genres": ["rock", "alternative"],
        "instruments": ["guitar", "vocals"],
        "experience_years": 5,
        "influences": ["Nirvana", "Radiohead"],
        "achievements": ["Local band of the year 2023"]
    }


@pytest.fixture
def sample_venue_data():
    """Sample venue data for testing."""
    return {
        "email": "venue@example.com",
        "username": "testvenue",
        "password": "venuepass123",
        "display_name": "Test Venue",
        "role": "venue",
        "venue_name": "The Test Club",
        "capacity": 200,
        "address": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "country": "Test Country",
        "venue_type": "club",
        "amenities": ["stage", "sound_system", "bar"]
    }


@pytest.fixture
def sample_show_data():
    """Sample show data for testing."""
    return {
        "title": "Test Show",
        "description": "A test show for testing purposes",
        "venue_id": "test-venue-id",
        "promoter_id": "test-promoter-id",
        "date": "2024-01-15T20:00:00Z",
        "doors_open": "2024-01-15T19:00:00Z",
        "show_start": "2024-01-15T20:30:00Z",
        "show_end": "2024-01-15T23:00:00Z",
        "ticket_price": 15.00,
        "ticket_url": "https://example.com/tickets",
        "poster_url": "https://example.com/poster.jpg",
        "genres": ["rock", "alternative"],
        "age_restriction": "18+",
        "capacity": 150
    }


@pytest.fixture
def sample_music_track_data():
    """Sample music track data for testing."""
    return {
        "title": "Test Song",
        "album": "Test Album",
        "genres": ["rock", "alternative"],
        "is_explicit": False,
        "release_date": "2024-01-01"
    }


@pytest.fixture
def sample_playlist_data():
    """Sample playlist data for testing."""
    return {
        "name": "Test Playlist",
        "description": "A test playlist for testing purposes",
        "is_public": True,
        "cover_image_url": "https://example.com/cover.jpg"
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNTE2MjM5MDIyfQ.test_signature"


@pytest.fixture
def mock_auth_headers(mock_jwt_token):
    """Mock authentication headers for testing."""
    return {"Authorization": f"Bearer {mock_jwt_token}"}


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_client.auth.get_user.return_value = Mock(
        user=Mock(
            id="test-user-id",
            email="test@example.com",
            user_metadata={"username": "testuser", "role": "user"}
        )
    )
    return mock_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    yield
    # Clean up after tests
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    if "DEBUG" in os.environ:
        del os.environ["DEBUG"]
