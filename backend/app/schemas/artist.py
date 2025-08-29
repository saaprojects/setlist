"""
Artist Pydantic schemas.
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class ArtistCreate(BaseModel):
    """Artist creation schema."""
    email: EmailStr
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


class UserResponse(BaseModel):
    """User response schema for artist registration."""
    id: int
    email: EmailStr
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


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


class ArtistRegistrationResponse(BaseModel):
    """Artist registration response schema."""
    user: UserResponse
    artist_profile: ArtistResponse
    access_token: str
    refresh_token: str
