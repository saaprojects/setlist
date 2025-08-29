"""
Pytest configuration and fixtures.
"""

import warnings
import pytest

# No specific warnings to suppress - using modern libraries

# Configure pytest
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "auth: Authentication related tests")
    config.addinivalue_line("markers", "users: User management tests")
    config.addinivalue_line("markers", "artists: Artist related tests")
    config.addinivalue_line("markers", "venues: Venue related tests")
    config.addinivalue_line("markers", "shows: Show management tests")
    config.addinivalue_line("markers", "music: Music content tests")
    config.addinivalue_line("markers", "playlists: Playlist management tests")
