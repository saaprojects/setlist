import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { authApi } from '@/api/auth'
import { useQueryClient } from 'react-query'

interface ArtistProfileForm {
  bio: string
  genres: string[]
  instruments: string[]
  location: string
  website: string
}

const VALID_GENRES = [
  'rock', 'pop', 'jazz', 'blues', 'country', 'electronic', 'hip-hop', 
  'classical', 'folk', 'metal', 'punk', 'reggae', 'r&b', 'soul', 
  'alternative', 'indie', 'funk', 'disco', 'house', 'techno', 'dubstep'
]

const COMMON_INSTRUMENTS = [
  'guitar', 'bass', 'drums', 'piano', 'keyboard', 'vocals', 'saxophone',
  'trumpet', 'trombone', 'violin', 'cello', 'flute', 'clarinet', 'harmonica',
  'banjo', 'mandolin', 'accordion', 'synthesizer', 'sampler', 'turntables'
]

export const EditArtistProfilePage: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [formData, setFormData] = useState<ArtistProfileForm>({
    bio: '',
    genres: [],
    instruments: [],
    location: '',
    website: ''
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Partial<ArtistProfileForm>>({})
  const [customGenre, setCustomGenre] = useState('')
  const [customInstrument, setCustomInstrument] = useState('')

  // Redirect if not authenticated or not an artist
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login')
    } else if (!isLoading && isAuthenticated && user && user.role !== 'artist') {
      navigate('/artist/profile')
    }
  }, [isAuthenticated, user, isLoading, navigate])

  // Load existing profile data (for now, we'll use placeholder data)
  useEffect(() => {
    if (user) {
      // TODO: Fetch actual profile data from backend
      setFormData({
        bio: user.bio || '',
        genres: user.genres || [],
        instruments: user.instruments || [],
        location: user.location || '',
        website: user.website || ''
      })
    }
  }, [user])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (errors[name as keyof ArtistProfileForm]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }))
    }
  }

  const addGenre = (genre: string) => {
    if (genre && !formData.genres.includes(genre)) {
      setFormData(prev => ({
        ...prev,
        genres: [...prev.genres, genre]
      }))
    }
    setCustomGenre('')
  }

  const removeGenre = (genreToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      genres: prev.genres.filter(genre => genre !== genreToRemove)
    }))
  }

  const addInstrument = (instrument: string) => {
    if (instrument && !formData.instruments.includes(instrument)) {
      setFormData(prev => ({
        ...prev,
        instruments: [...prev.instruments, instrument]
      }))
    }
    setCustomInstrument('')
  }

  const removeInstrument = (instrumentToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      instruments: prev.instruments.filter(instrument => instrument !== instrumentToRemove)
    }))
  }

  const validateForm = (): boolean => {
    const newErrors: Partial<ArtistProfileForm> = {}

    if (formData.bio.length > 500) {
      newErrors.bio = 'Bio must be 500 characters or less'
    }

    if (formData.website && !/^https?:\/\/.+/.test(formData.website)) {
      newErrors.website = 'Website must start with http:// or https://'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    if (!user) {
      console.error('No user data available')
      return
    }

    setIsSubmitting(true)
    
    try {
      // Call backend API to update profile
      const updatedUser = await authApi.updateProfile(user.id, {
        bio: formData.bio,
        genres: formData.genres,
        instruments: formData.instruments,
        location: formData.location,
        website: formData.website
      })
      
      console.log('Profile updated successfully:', updatedUser)
      
      // Invalidate the auth query to refresh user data
      queryClient.invalidateQueries('auth-user')
      
      // Redirect back to profile page
      navigate('/artist/profile')
    } catch (error) {
      console.error('Failed to update profile:', error)
      // TODO: Show error message to user
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  // Only redirect if we're certain the user shouldn't be here
  if (!isLoading && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="mb-4">You must be logged in to view this page.</p>
          <button 
            onClick={() => navigate('/login')} 
            className="btn btn-primary"
          >
            Go to Login
          </button>
        </div>
      </div>
    )
  }

  if (!isLoading && isAuthenticated && user && user.role !== 'artist') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="mb-4">This page is only available to artists.</p>
          <button 
            onClick={() => navigate('/artist/profile')} 
            className="btn btn-primary"
          >
            Go to Profile
          </button>
        </div>
      </div>
    )
  }

  // Don't render the form until we have user data
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading user data...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-neutral-900">Edit Artist Profile</h1>
            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/artist/profile')}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                form="profile-form"
                disabled={isSubmitting}
                className="btn btn-primary"
              >
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form id="profile-form" onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="card">
            <div className="card-content">
              <h3 className="text-lg font-semibold text-neutral-900 mb-6">Basic Information</h3>
              
              {/* Bio */}
              <div className="mb-6">
                <label htmlFor="bio" className="block text-sm font-medium text-neutral-700 mb-2">
                  Bio
                </label>
                <textarea
                  name="bio"
                  id="bio"
                  rows={4}
                  value={formData.bio}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    errors.bio ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Tell us about yourself, your music, and your style..."
                />
                <div className="flex justify-between items-center mt-1">
                  {errors.bio && (
                    <p className="text-sm text-red-600">{errors.bio}</p>
                  )}
                  <p className="text-sm text-neutral-500 ml-auto">
                    {formData.bio.length}/500
                  </p>
                </div>
              </div>

              {/* Location */}
              <div className="mb-6">
                <label htmlFor="location" className="block text-sm font-medium text-neutral-700 mb-2">
                  Location
                </label>
                <input
                  name="location"
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="City, State or Country"
                />
              </div>

              {/* Website */}
              <div>
                <label htmlFor="website" className="block text-sm font-medium text-neutral-700 mb-2">
                  Website
                </label>
                <input
                  name="website"
                  id="website"
                  type="url"
                  value={formData.website}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    errors.website ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="https://yourwebsite.com"
                />
                {errors.website && (
                  <p className="mt-1 text-sm text-red-600">{errors.website}</p>
                )}
              </div>
            </div>
          </div>

          {/* Music Genres */}
          <div className="card">
            <div className="card-content">
              <h3 className="text-lg font-semibold text-neutral-900 mb-6">Music Genres</h3>
              
              {/* Selected Genres */}
              {formData.genres.length > 0 && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Selected Genres
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {formData.genres.map(genre => (
                      <span
                        key={genre}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                      >
                        {genre}
                        <button
                          type="button"
                          onClick={() => removeGenre(genre)}
                          className="ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full text-primary-400 hover:bg-primary-200 hover:text-primary-500"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Add Genre */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Add Genre
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customGenre}
                    onChange={(e) => setCustomGenre(e.target.value)}
                    className="flex-1 px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Type a genre or select from list"
                  />
                  <button
                    type="button"
                    onClick={() => addGenre(customGenre)}
                    className="btn btn-secondary"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Popular Genres */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Popular Genres
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {VALID_GENRES.map(genre => (
                    <button
                      key={genre}
                      type="button"
                      onClick={() => addGenre(genre)}
                      disabled={formData.genres.includes(genre)}
                      className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                        formData.genres.includes(genre)
                          ? 'bg-primary-100 border-primary-300 text-primary-800 cursor-not-allowed'
                          : 'bg-white border-neutral-300 text-neutral-700 hover:bg-neutral-50 hover:border-primary-300'
                      }`}
                    >
                      {genre}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Instruments */}
          <div className="card">
            <div className="card-content">
              <h3 className="text-lg font-semibold text-neutral-900 mb-6">Instruments</h3>
              
              {/* Selected Instruments */}
              {formData.instruments.length > 0 && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Selected Instruments
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {formData.instruments.map(instrument => (
                      <span
                        key={instrument}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-secondary-100 text-secondary-800"
                      >
                        {instrument}
                        <button
                          type="button"
                          onClick={() => removeInstrument(instrument)}
                          className="ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full text-secondary-400 hover:bg-secondary-200 hover:text-secondary-500"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Add Instrument */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Add Instrument
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customInstrument}
                    onChange={(e) => setCustomInstrument(e.target.value)}
                    className="flex-1 px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Type an instrument or select from list"
                  />
                  <button
                    type="button"
                    onClick={() => addInstrument(customInstrument)}
                    className="btn btn-secondary"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Common Instruments */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Common Instruments
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {COMMON_INSTRUMENTS.map(instrument => (
                    <button
                      key={instrument}
                      type="button"
                      onClick={() => addInstrument(instrument)}
                      disabled={formData.instruments.includes(instrument)}
                      className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                        formData.instruments.includes(instrument)
                          ? 'bg-secondary-100 border-secondary-300 text-secondary-800 cursor-not-allowed'
                          : 'bg-white border-neutral-300 text-neutral-700 hover:bg-neutral-50 hover:border-secondary-300'
                      }`}
                    >
                      {instrument}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
