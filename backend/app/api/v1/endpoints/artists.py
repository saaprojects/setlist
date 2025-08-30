"""
Artist-specific endpoints for the Setlist application.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user, oauth2_scheme
from app.models.artist import ArtistProfile, Collaboration
from app.models.music import MusicTrack
from app.models.user import User, UserRole
from app.schemas.artist import (
    ArtistCreate, ArtistUpdate, ArtistResponse, UserResponse,
    MusicTrackCreate, MusicTrackUpdate, MusicTrackResponse,
    CollaborationCreate, CollaborationUpdate, CollaborationResponse, ArtistProfileResponse
)

router = APIRouter()


async def _get_authenticated_artist(token: str, db: Session) -> User:
    """Helper function to get the authenticated artist user."""
    user = await get_current_user(token, db)
    if user.role != UserRole.artist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only artists can access this resource"
        )
    return user


@router.get("/me", response_model=ArtistProfileResponse)
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
    
    # Create response with both user and profile info
    response_data = {
        "user": user,
        "bio": artist_profile.bio,
        "genres": artist_profile.genres,
        "instruments": artist_profile.instruments,
        "location": artist_profile.location,
        "website": artist_profile.website,
        "created_at": artist_profile.created_at,
        "updated_at": artist_profile.updated_at,
    }
    
    return ArtistProfileResponse.model_validate(response_data)


@router.put("/me", response_model=ArtistProfileResponse)
async def update_artist_profile(
    artist_update: ArtistUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update current artist's profile.
    
    This endpoint allows authenticated artists to update their profile details.
    """
    user = await _get_authenticated_artist(token, db)
    
    artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
    
    if not artist_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    # Update fields
    if artist_update.bio is not None:
        artist_profile.bio = artist_update.bio
    if artist_update.genres is not None:
        artist_profile.genres = artist_update.genres
    if artist_update.instruments is not None:
        artist_profile.instruments = artist_update.instruments
    if artist_update.location is not None:
        artist_profile.location = artist_update.location
    if artist_update.website is not None:
        artist_profile.website = artist_update.website
    
    db.commit()
    db.refresh(artist_profile)
    
    # Create response with both user and profile info
    response_data = {
        "user": user,
        "bio": artist_profile.bio,
        "genres": artist_profile.genres,
        "instruments": artist_profile.instruments,
        "location": artist_profile.location,
        "website": artist_profile.website,
        "created_at": artist_profile.created_at,
        "updated_at": artist_profile.updated_at,
    }
    
    return ArtistProfileResponse.model_validate(response_data)


@router.post("/me/profile-picture", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture for the current artist.
    
    This endpoint allows artists to upload a profile picture.
    """
    # Validate file type (only images)
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only image files are allowed."
        )
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    user = await _get_authenticated_artist(token, db)
    
    # Get artist profile
    artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
    
    if not artist_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Store binary data and content type in database
    artist_profile.profile_picture_binary = file_content
    artist_profile.profile_picture_content_type = file.content_type
    
    db.commit()
    db.refresh(artist_profile)
    
    return {
        "message": "Profile picture uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(file_content)
    }


@router.get("/profile-picture/{user_id}")
async def get_profile_picture(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user's profile picture.
    
    This endpoint returns the profile picture binary data with proper content type headers.
    """
    # Get artist profile
    artist_profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user_id).first()
    
    if not artist_profile or not artist_profile.profile_picture_binary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture not found"
        )
    
    # Return the binary data with proper content type
    return Response(
        content=artist_profile.profile_picture_binary,
        media_type=artist_profile.profile_picture_content_type,
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": f"inline; filename=profile_picture_{user_id}"
        }
    )


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
    # Build query for active artists
    query = db.query(ArtistProfile).join(User).filter(User.is_active == True)
    
    # Get all artists first, then filter in Python
    artists = query.all()
    
    # Filter by genre if specified
    if genre:
        artists = [artist for artist in artists if artist.genres and genre in artist.genres]
    
    # Filter by location if specified
    if location:
        artists = [artist for artist in artists if artist.location and location.lower() in artist.location.lower()]
    
    # Filter by instrument if specified
    if instrument:
        artists = [artist for artist in artists if artist.instruments and instrument in artist.instruments]
    
    # Apply pagination
    total_artists = len(artists)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    artists = artists[start_idx:end_idx]
    
    # Calculate pagination info
    total_pages = (total_artists + limit - 1) // limit
    
    return {
        "artists": [ArtistResponse.model_validate(artist) for artist in artists],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_artists,
            "pages": total_pages
        }
    }


# Music Track Management Endpoints

@router.post("/me/tracks", response_model=MusicTrackResponse, status_code=status.HTTP_201_CREATED)
async def upload_music_track(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    is_public: bool = Form(True),
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
        title=title,
        description=description,
        genre=genre,
        tags=tags,
        audio_url=audio_url,
        is_public=is_public
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
    
    # Create new collaboration request
    new_collaboration = Collaboration(
        requester_id=user.id,
        target_artist_id=collaboration_data.target_artist_id,
        message=collaboration_data.message,
        project_type=collaboration_data.project_type,
        status="pending"
    )
    
    db.add(new_collaboration)
    db.commit()
    db.refresh(new_collaboration)
    
    return CollaborationResponse.model_validate(new_collaboration)


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
