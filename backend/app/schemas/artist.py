"""
Artist Pydantic schemas.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ArtistCreate(BaseModel):
    """Artist creation schema."""
    email: str
    username: str
    password: str
    display_name: str
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None


class ArtistUpdate(BaseModel):
    """Artist update schema."""
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None


class ArtistResponse(BaseModel):
    """Artist response schema."""
    id: int
    user_id: int
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
