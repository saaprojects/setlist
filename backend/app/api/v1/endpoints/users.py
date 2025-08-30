"""
User management endpoints for profile operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.artist import ArtistProfile
from app.core.security import get_current_user

router = APIRouter()


class UserProfileUpdate(BaseModel):
    """User profile update model."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[dict] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None


class UserProfileResponse(BaseModel):
    """User profile response model."""
    id: str
    username: str
    email: str
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]
    website: Optional[str]
    social_links: dict
    role: str
    is_verified: bool
    is_active: bool
    created_at: str
    updated_at: str
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None


@router.get("/", response_model=List[UserProfileResponse])
async def get_users():
    """
    Get list of all users.
    
    This endpoint returns a paginated list of all users in the system.
    """
    # TODO: Implement user listing logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User listing not yet implemented"
    )


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: str):
    """
    Get user profile by ID.
    
    This endpoint returns the profile of a specific user.
    """
    # TODO: Implement user retrieval logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User retrieval not yet implemented"
    )


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user(
    user_id: str, 
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile.
    
    This endpoint allows users to update their profile information.
    """
    # Check if user is updating their own profile
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    try:
        # Update User model fields
        user_update_data = {}
        if profile_data.display_name is not None:
            user_update_data["display_name"] = profile_data.display_name
        
        if user_update_data:
            db.query(User).filter(User.id == current_user.id).update(user_update_data)
        
        # Handle ArtistProfile updates (for artists)
        if current_user.role == "artist":
            # Check if profile exists
            artist_profile = db.query(ArtistProfile).filter(
                ArtistProfile.user_id == current_user.id
            ).first()
            
            if not artist_profile:
                # Create new profile
                artist_profile = ArtistProfile(
                    user_id=current_user.id,
                    bio=profile_data.bio,
                    genres=profile_data.genres,
                    instruments=profile_data.instruments,
                    location=profile_data.location,
                    website=profile_data.website
                )
                db.add(artist_profile)
            else:
                # Update existing profile
                if profile_data.bio is not None:
                    artist_profile.bio = profile_data.bio
                if profile_data.genres is not None:
                    artist_profile.genres = profile_data.genres
                if profile_data.instruments is not None:
                    artist_profile.instruments = profile_data.instruments
                if profile_data.location is not None:
                    artist_profile.location = profile_data.location
                if profile_data.website is not None:
                    artist_profile.website = profile_data.website
        
        # Commit changes
        db.commit()
        
        # Refresh user data
        db.refresh(current_user)
        if current_user.role == "artist" and artist_profile:
            db.refresh(artist_profile)
        
        # Build response
        response_data = {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "display_name": current_user.display_name,
            "bio": None,
            "avatar_url": None,
            "location": None,
            "website": None,
            "social_links": {},
            "role": current_user.role,
            "is_verified": False,  # TODO: Implement verification
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat(),
            "genres": None,
            "instruments": None
        }
        
        # Add artist profile data if available
        if current_user.role == "artist" and artist_profile:
            response_data.update({
                "bio": artist_profile.bio,
                "location": artist_profile.location,
                "website": artist_profile.website,
                "genres": artist_profile.genres,
                "instruments": artist_profile.instruments
            })
        
        return response_data
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """
    Delete user account.
    
    This endpoint permanently deletes a user account.
    """
    # TODO: Implement user deletion logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User deletion not yet implemented"
    )
