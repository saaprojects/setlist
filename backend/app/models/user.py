"""
User model - the foundation for all user types.
"""

from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration."""
    user = "user"
    artist = "artist"
    promoter = "promoter"
    venue = "venue"


class User(BaseModel):
    """User model - foundation for all user types."""
    
    __tablename__ = "users"
    
    # Required fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    artist_profile = relationship("ArtistProfile", back_populates="user", uselist=False)
    music_tracks = relationship("MusicTrack", back_populates="artist")
    sent_collaborations = relationship("Collaboration", foreign_keys="Collaboration.requester_id", back_populates="requester")
    received_collaborations = relationship("Collaboration", foreign_keys="Collaboration.target_artist_id", back_populates="target_artist")
