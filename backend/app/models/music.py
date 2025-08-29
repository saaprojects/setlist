"""
Music track models.
"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class MusicTrack(BaseModel):
    """Music track model."""
    
    __tablename__ = "music_tracks"
    
    # Foreign key to artist (user)
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Track information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=False)
    tags = Column(Text, nullable=True)  # JSON string for now
    
    # File information
    audio_url = Column(String(500), nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    file_size = Column(Integer, nullable=True)  # File size in bytes
    
    # Visibility
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    artist = relationship("User", back_populates="music_tracks")
