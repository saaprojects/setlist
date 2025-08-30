"""
Database configuration and connection setup.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings
from ..models.base import Base

# Create SQLAlchemy engine
engine = create_engine(
    settings.SUPABASE_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    # For development, we might want to echo SQL queries
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is now imported from models.base

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables in the database (DANGER: development only)."""
    Base.metadata.drop_all(bind=engine)
