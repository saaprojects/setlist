import React from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Link } from 'react-router-dom'

export const ArtistProfilePage: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="mb-4">You must be logged in to view this page.</p>
          <Link to="/login" className="btn btn-primary">
            Go to Login
          </Link>
        </div>
      </div>
    )
  }

  if (user.role !== 'artist') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="mb-4">This page is only available to artists.</p>
          <Link to="/" className="btn btn-primary">
            Go Home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-neutral-900">Artist Profile</h1>
            <div className="flex space-x-4">
              <Link to="/" className="btn btn-secondary">
                Home
              </Link>
              <Link to="/artist/profile/edit" className="btn btn-primary">
                Edit Profile
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="card-content">
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto mb-4 bg-neutral-200 rounded-full flex items-center justify-center">
                    <span className="text-4xl text-neutral-500">
                      {user.display_name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                    {user.display_name}
                  </h2>
                  <p className="text-neutral-600 mb-4">@{user.username}</p>
                  <p className="text-sm text-neutral-500 mb-4">
                    Member since {new Date(user.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <div className="card">
              <div className="card-content">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button className="btn btn-primary w-full">
                    Upload Music Track
                  </button>
                  <button className="btn btn-secondary w-full">
                    Find Collaborators
                  </button>
                  <button className="btn btn-secondary w-full">
                    View My Tracks
                  </button>
                  <button className="btn btn-secondary w-full">
                    Manage Collaborations
                  </button>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <div className="card-content">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recent Activity</h3>
                <div className="text-center py-8 text-neutral-500">
                  <p>No recent activity to display.</p>
                  <p className="text-sm mt-2">Start by uploading your first track!</p>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="card">
              <div className="card-content">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Your Stats</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-primary-600">0</div>
                    <div className="text-sm text-neutral-600">Tracks</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary-600">0</div>
                    <div className="text-sm text-neutral-600">Collaborations</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary-600">0</div>
                    <div className="text-sm text-neutral-600">Followers</div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Profile Information */}
            <div className="card">
              <div className="card-content">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Profile Information</h3>
                
                {/* Bio */}
                {user.bio && (
                  <div className="mb-4">
                    <h4 className="font-medium text-neutral-900 mb-2">Bio</h4>
                    <p className="text-neutral-700 whitespace-pre-wrap">{user.bio}</p>
                  </div>
                )}
                
                {/* Location */}
                {user.location && (
                  <div className="mb-4">
                    <h4 className="font-medium text-neutral-900 mb-2">Location</h4>
                    <p className="text-neutral-700">{user.location}</p>
                  </div>
                )}
                
                {/* Website */}
                {user.website && (
                  <div className="mb-4">
                    <h4 className="font-medium text-neutral-900 mb-2">Website</h4>
                    <a 
                      href={user.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-800 underline"
                    >
                      {user.website}
                    </a>
                  </div>
                )}
                
                {/* Show message if no profile info */}
                {!user.bio && !user.location && !user.website && (
                  <div className="text-center py-6 text-neutral-500">
                    <p>No profile information yet.</p>
                    <p className="text-sm mt-2">Click "Edit Profile" to add your bio, location, and website.</p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Genres */}
            {user.genres && user.genres.length > 0 && (
              <div className="card mt-4">
                <div className="card-content">
                  <h4 className="font-medium text-neutral-900 mb-3">Genres</h4>
                  <div className="flex flex-wrap gap-2">
                    {user.genres.map(genre => (
                      <span
                        key={genre}
                        className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {/* Instruments */}
            {user.instruments && user.instruments.length > 0 && (
              <div className="card mt-4">
                <div className="card-content">
                  <h4 className="font-medium text-neutral-900 mb-3">Instruments</h4>
                  <div className="flex flex-wrap gap-2">
                    {user.instruments.map(instrument => (
                      <span
                        key={instrument}
                        className="px-2 py-1 bg-secondary-100 text-secondary-800 text-xs rounded-full"
                      >
                        {instrument}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
