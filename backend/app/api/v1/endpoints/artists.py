"""
Artist endpoints for registration, profile management, and discovery.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.artist import ArtistProfile
from app.schemas.artist import ArtistCreate, ArtistUpdate, ArtistResponse, ArtistRegistrationResponse, UserResponse
from app.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=ArtistRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_artist(artist_data: ArtistCreate, db: Session = Depends(get_db)):
    """
    Register a new artist.
    
    This endpoint allows artists to create new accounts with profile information.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == artist_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == artist_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate password strength (minimum 8 characters)
    if len(artist_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )
    
    # Create new user with artist role
    hashed_password = get_password_hash(artist_data.password)
    new_user = User(
        email=artist_data.email,
        username=artist_data.username,
        password_hash=hashed_password,
        display_name=artist_data.display_name,
        role=UserRole.artist,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create artist profile
    artist_profile = ArtistProfile(
        user_id=new_user.id,
        bio=artist_data.bio,
        genres=artist_data.genres,
        instruments=artist_data.instruments
    )
    
    db.add(artist_profile)
    db.commit()
    db.refresh(artist_profile)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.username})
    refresh_token = create_access_token(data={"sub": new_user.username}, expires_delta=None)
    
    return ArtistRegistrationResponse(
        user=UserResponse.model_validate(new_user),
        artist_profile=ArtistResponse.model_validate(artist_profile),
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=ArtistResponse)
async def get_artist_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current artist's profile.
    
    This endpoint returns the profile of the currently authenticated artist.
    """
    try:
        # Decode the JWT token to get user information
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import JWTError, jwt
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    if user.role != UserRole.artist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only artists can access this endpoint"
        )
    
    # Get artist profile
    artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
    
    if not artist_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    return ArtistResponse.model_validate(artist_profile)


@router.put("/me", response_model=ArtistResponse)
async def update_artist_profile(
    profile_update: ArtistUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update current artist's profile.
    
    This endpoint allows artists to update their profile information.
    """
    try:
        # Decode the JWT token to get user information
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import JWTError, jwt
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    if user.role != UserRole.artist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only artists can access this endpoint"
        )
    
    # Get artist profile
    artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
    
    if not artist_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    # Update profile fields
    if profile_update.bio is not None:
        artist_profile.bio = profile_update.bio
    if profile_update.genres is not None:
        artist_profile.genres = profile_update.genres
    if profile_update.instruments is not None:
        artist_profile.instruments = profile_update.instruments
    if profile_update.location is not None:
        artist_profile.location = profile_update.location
    if profile_update.website is not None:
        artist_profile.website = profile_update.website
    
    db.commit()
    db.refresh(artist_profile)
    
    return ArtistResponse.model_validate(artist_profile)


@router.post("/me/profile-picture", response_model=dict)
async def upload_profile_picture(
    profile_picture: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Upload artist profile picture.
    
    This endpoint allows artists to upload a profile picture.
    """
    # Validate file type
    if not profile_picture.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only images are allowed."
        )
    
    # Validate file size (max 5MB)
    if profile_picture.size and profile_picture.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    try:
        # Decode the JWT token to get user information
        from app.core.security import SECRET_KEY, ALGORITHM
        from jose import JWTError, jwt
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    if user.role != UserRole.artist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only artists can access this endpoint"
        )
    
    # For now, return a mock URL (in production, you'd upload to S3/cloud storage)
    profile_picture_url = f"https://example.com/profile-pictures/{user.username}.jpg"
    
    return {"profile_picture_url": profile_picture_url}


@router.get("/search", response_model=dict)
async def search_artists(
    genre: Optional[str] = None,
    location: Optional[str] = None,
    instrument: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search for artists by various criteria.
    
    This endpoint allows users to discover artists based on genre, location, or instrument.
    """
    # Build query
    query = db.query(ArtistProfile).join(User).filter(User.is_active == True)
    
    if genre:
        query = query.filter(ArtistProfile.genres.contains(genre))
    if location:
        query = query.filter(ArtistProfile.location.contains(location))
    if instrument:
        query = query.filter(ArtistProfile.instruments.contains(instrument))
    
    # Pagination
    offset = (page - 1) * limit
    total = query.count()
    artists = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    artist_list = []
    for artist in artists:
        artist_data = {
            "id": artist.id,
            "user_id": artist.user_id,
            "display_name": artist.user.display_name,
            "username": artist.user.username,
            "bio": artist.bio,
            "genres": artist.genres if artist.genres else [],
            "instruments": artist.instruments if artist.instruments else [],
            "location": artist.location,
            "website": artist.website,
            "created_at": artist.created_at.isoformat(),
            "updated_at": artist.updated_at.isoformat()
        }
        artist_list.append(artist_data)
    
    return {
        "artists": artist_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }
