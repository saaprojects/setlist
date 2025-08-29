"""
Artist database models.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON, Boolean, LargeBinary
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
    
    # Profile picture as binary data
    profile_picture_binary = Column(LargeBinary, nullable=True)
    profile_picture_content_type = Column(String(100), nullable=True)  # e.g., "image/jpeg"
    
    # Relationships
    user = relationship("User", back_populates="artist_profile")


class Collaboration(BaseModel):
    """Artist collaboration model."""
    
    __tablename__ = "collaborations"
    
    # Foreign keys
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_artist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Collaboration details
    message = Column(Text, nullable=False)
    project_type = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")  # pending, accepted, declined
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_collaborations")
    target_artist = relationship("User", foreign_keys=[target_artist_id], back_populates="received_collaborations")
