"""
Test database setup and model imports.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all models can be imported."""
    try:
        from app.models import Base, User, UserRole, ArtistProfile, MusicTrack
        print("✅ All models imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    try:
        from app.core.database import engine
        from app.core.config import settings
        from sqlalchemy import text
        
        print(f"🔗 Database URL: {settings.DATABASE_URL}")
        
        # Try to connect using proper SQLAlchemy 2.0 syntax
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_model_metadata():
    """Test that models have proper metadata."""
    try:
        from app.models import Base
        
        print(f"📋 Tables in metadata: {list(Base.metadata.tables.keys())}")
        
        # Check that our expected tables exist
        expected_tables = {'users', 'artist_profiles', 'music_tracks'}
        actual_tables = set(Base.metadata.tables.keys())
        
        if expected_tables.issubset(actual_tables):
            print("✅ All expected tables found in metadata!")
            return True
        else:
            missing = expected_tables - actual_tables
            print(f"❌ Missing tables: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Model metadata test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing database setup...")
    print()
    
    success = True
    
    success &= test_imports()
    print()
    
    success &= test_database_connection()
    print()
    
    success &= test_model_metadata()
    print()
    
    if success:
        print("🎉 All tests passed! Database setup is ready.")
    else:
        print("💥 Some tests failed. Check the errors above.")
        sys.exit(1)
