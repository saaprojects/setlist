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
from app.models.artist import ArtistProfile, Collaboration
from app.models.music import MusicTrack
from app.schemas.artist import (
    ArtistCreate, ArtistUpdate, ArtistResponse, ArtistRegistrationResponse, UserResponse,
    MusicTrackCreate, MusicTrackUpdate, MusicTrackResponse,
    CollaborationCreate, CollaborationUpdate, CollaborationResponse, ArtistProfileResponse
)
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
    user = await _get_authenticated_artist(token, db)
    
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
    user = await _get_authenticated_artist(token, db)
    
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
    
    user = await _get_authenticated_artist(token, db)
    
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
        # Use PostgreSQL JSON containment operator for genres
        query = query.filter(ArtistProfile.genres.contains([genre]))
    if location:
        # Use LIKE for text search in location
        query = query.filter(ArtistProfile.location.contains(location))
    if instrument:
        # Use PostgreSQL JSON containment operator for instruments
        query = query.filter(ArtistProfile.instruments.contains([instrument]))
    
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


# Music Track Management Endpoints

@router.post("/me/tracks", response_model=MusicTrackResponse, status_code=status.HTTP_201_CREATED)
async def upload_music_track(
    track_data: MusicTrackCreate,
    audio_file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Upload a new music track.
    
    This endpoint allows artists to upload music tracks.
    """
    # Validate file type
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only audio files are allowed."
        )
    
    # Validate file size (max 50MB)
    if audio_file.size and audio_file.size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 50MB."
        )
    
    # Get authenticated user
    user = await _get_authenticated_artist(token, db)
    
    # For now, return a mock URL (in production, you'd upload to S3/cloud storage)
    audio_url = f"https://example.com/audio/{user.username}/{audio_file.filename}"
    
    # Create music track
    music_track = MusicTrack(
        artist_id=user.id,
        title=track_data.title,
        description=track_data.description,
        genre=track_data.genre,
        tags=track_data.tags,
        audio_url=audio_url,
        is_public=track_data.is_public
    )
    
    db.add(music_track)
    db.commit()
    db.refresh(music_track)
    
    return MusicTrackResponse.model_validate(music_track)


@router.get("/me/tracks", response_model=dict)
async def get_artist_tracks(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current artist's tracks.
    
    This endpoint returns all tracks by the currently authenticated artist.
    """
    user = await _get_authenticated_artist(token, db)
    
    tracks = db.query(MusicTrack).filter(MusicTrack.artist_id == user.id).all()
    
    track_list = [MusicTrackResponse.model_validate(track) for track in tracks]
    
    return {"tracks": track_list}


@router.put("/me/tracks/{track_id}", response_model=MusicTrackResponse)
async def update_music_track(
    track_id: int,
    track_update: MusicTrackUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update a music track.
    
    This endpoint allows artists to update their track information.
    """
    user = await _get_authenticated_artist(token, db)
    
    # Find track and verify ownership
    track = db.query(MusicTrack).filter(
        MusicTrack.id == track_id,
        MusicTrack.artist_id == user.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Update track fields
    if track_update.title is not None:
        track.title = track_update.title
    if track_update.description is not None:
        track.description = track_update.description
    if track_update.genre is not None:
        track.genre = track_update.genre
    if track_update.tags is not None:
        track.tags = track_update.tags
    if track_update.is_public is not None:
        track.is_public = track_update.is_public
    
    db.commit()
    db.refresh(track)
    
    return MusicTrackResponse.model_validate(track)


@router.delete("/me/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_music_track(
    track_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Delete a music track.
    
    This endpoint allows artists to delete their tracks.
    """
    user = await _get_authenticated_artist(token, db)
    
    # Find track and verify ownership
    track = db.query(MusicTrack).filter(
        MusicTrack.id == track_id,
        MusicTrack.artist_id == user.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    db.delete(track)
    db.commit()
    
    return None


# Collaboration Endpoints

@router.post("/collaborations", response_model=CollaborationResponse, status_code=status.HTTP_201_CREATED)
async def send_collaboration_request(
    collaboration_data: CollaborationCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Send a collaboration request to another artist.
    
    This endpoint allows artists to send collaboration requests.
    """
    user = await _get_authenticated_artist(token, db)
    
    # Check if target artist exists and is an artist
    target_artist = db.query(User).filter(
        User.id == collaboration_data.target_artist_id,
        User.role == UserRole.artist,
        User.is_active == True
    ).first()
    
    if not target_artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target artist not found"
        )
    
    # Check if collaboration already exists
    existing_collab = db.query(Collaboration).filter(
        Collaboration.requester_id == user.id,
        Collaboration.target_artist_id == collaboration_data.target_artist_id,
        Collaboration.status == "pending"
    ).first()
    
    if existing_collab:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collaboration request already sent"
        )
    
    # Create collaboration request
    collaboration = Collaboration(
        requester_id=user.id,
        target_artist_id=collaboration_data.target_artist_id,
        message=collaboration_data.message,
        project_type=collaboration_data.project_type,
        status="pending"
    )
    
    db.add(collaboration)
    db.commit()
    db.refresh(collaboration)
    
    return CollaborationResponse.model_validate(collaboration)


@router.get("/collaborations", response_model=dict)
async def get_collaboration_requests(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get collaboration requests for the current artist.
    
    This endpoint returns both sent and received collaboration requests.
    """
    user = await _get_authenticated_artist(token, db)
    
    # Get sent collaborations
    sent_collaborations = db.query(Collaboration).filter(
        Collaboration.requester_id == user.id
    ).all()
    
    # Get received collaborations
    received_collaborations = db.query(Collaboration).filter(
        Collaboration.target_artist_id == user.id
    ).all()
    
    return {
        "collaborations": {
            "sent": [CollaborationResponse.model_validate(c) for c in sent_collaborations],
            "received": [CollaborationResponse.model_validate(c) for c in received_collaborations]
        }
    }


@router.put("/collaborations/{collaboration_id}/accept", response_model=CollaborationResponse)
async def accept_collaboration_request(
    collaboration_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Accept a collaboration request.
    
    This endpoint allows artists to accept collaboration requests.
    """
    user = await _get_authenticated_artist(token, db)
    
    # Find collaboration and verify it's for this user
    collaboration = db.query(Collaboration).filter(
        Collaboration.id == collaboration_id,
        Collaboration.target_artist_id == user.id,
        Collaboration.status == "pending"
    ).first()
    
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration request not found"
        )
    
    collaboration.status = "accepted"
    db.commit()
    db.refresh(collaboration)
    
    return CollaborationResponse.model_validate(collaboration)


@router.put("/collaborations/{collaboration_id}/decline", response_model=CollaborationResponse)
async def decline_collaboration_request(
    collaboration_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Decline a collaboration request.
    
    This endpoint allows artists to decline collaboration requests.
    """
    user = await _get_authenticated_artist(token, db)
    
    # Find collaboration and verify it's for this user
    collaboration = db.query(Collaboration).filter(
        Collaboration.id == collaboration_id,
        Collaboration.target_artist_id == user.id,
        Collaboration.status == "pending"
    ).first()
    
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration request not found"
        )
    
    collaboration.status = "declined"
    db.commit()
    db.refresh(collaboration)
    
    return CollaborationResponse.model_validate(collaboration)


# Helper function to get authenticated artist
async def _get_authenticated_artist(token: str, db: Session) -> User:
    """Helper function to get the authenticated artist user."""
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
    
    return user
