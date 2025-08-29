"""
Artist database models.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class ArtistProfile(BaseModel):
    """Artist profile model."""
    
    __tablename__ = "artist_profiles"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Profile information
    bio = Column(Text, nullable=True)
    genres = Column(JSON, nullable=True)  # JSON array for genres
    instruments = Column(JSON, nullable=True)  # JSON array for instruments
    location = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="artist_profile")
