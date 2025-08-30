"""
Authentication schemas for the Setlist application.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole
from app.schemas.artist import ArtistProfileResponse


class UserCreate(BaseModel):
    """User creation request model."""
    email: EmailStr
    username: str
    password: str
    display_name: str
    role: UserRole


class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: EmailStr
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Profile fields (for artists)
    bio: Optional[str] = None
    genres: Optional[list] = None
    instruments: Optional[list] = None
    location: Optional[str] = None
    website: Optional[str] = None
    
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: UserResponse


class UserRegistrationResponse(BaseModel):
    """User registration response model."""
    user: UserResponse
    access_token: str
    refresh_token: str
    artist_profile: Optional[ArtistProfileResponse] = None
