import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { UserRole } from '@/types/auth'

interface RegisterFormData {
  email: string
  username: string
  password: string
  confirmPassword: string
  display_name: string
  role: UserRole
}

export const RegisterPage: React.FC = () => {
  const { register, isLoading, registerError } = useAuth()
  const [formErrors, setFormErrors] = useState<Partial<RegisterFormData>>({})
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    display_name: '',
    role: UserRole.ARTIST, // Default to artist for now
  })

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterFormData> = {}

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    // Username validation
    if (!formData.username) {
      newErrors.username = 'Username is required'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters long'
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      newErrors.username = 'Username can only contain letters, numbers, and underscores'
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long'
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    // Display name validation
    if (!formData.display_name) {
      newErrors.display_name = 'Display name is required'
    } else if (formData.display_name.length < 2) {
      newErrors.display_name = 'Display name must be at least 2 characters long'
    }

    setFormErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (formErrors[name as keyof RegisterFormData]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        display_name: formData.display_name,
        role: formData.role,
      })
      // Registration success will be handled by useAuth hook (redirect)
    } catch (err) {
      // Error handling is done by the useAuth hook
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-neutral-900">Join Setlist</h2>
          <p className="mt-2 text-sm text-neutral-600">
            Create your account and start building your music community.
          </p>
        </div>
        
        <div className="card">
          <div className="card-content">
            <form onSubmit={handleSubmit} className="space-y-6" role="form">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-2">
                  Email
                </label>
                <input
                  name="email"
                  id="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    formErrors.email ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Enter your email"
                />
                {formErrors.email && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.email}</p>
                )}
              </div>

              {/* Username Field */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-neutral-700 mb-2">
                  Username
                </label>
                <input
                  name="username"
                  id="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    formErrors.username ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Choose a username"
                />
                {formErrors.username && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.username}</p>
                )}
              </div>

              {/* Display Name Field */}
              <div>
                <label htmlFor="display_name" className="block text-sm font-medium text-neutral-700 mb-2">
                  Display Name
                </label>
                <input
                  name="display_name"
                  id="display_name"
                  type="text"
                  required
                  value={formData.display_name}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    formErrors.display_name ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Enter your display name"
                />
                {formErrors.display_name && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.display_name}</p>
                )}
              </div>

              {/* Role Selection */}
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-neutral-700 mb-2">
                  Account Type
                </label>
                <select
                  name="role"
                  id="role"
                  required
                  value={formData.role}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value={UserRole.ARTIST}>Artist / Musician</option>
                  <option value={UserRole.PROMOTER}>Promoter / Event Organizer</option>
                  <option value={UserRole.VENUE}>Venue / Club</option>
                  <option value={UserRole.USER}>Music Fan</option>
                </select>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-2">
                  Password
                </label>
                <input
                  name="password"
                  id="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    formErrors.password ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Create a password"
                />
                {formErrors.password && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.password}</p>
                )}
              </div>

              {/* Confirm Password Field */}
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-neutral-700 mb-2">
                  Confirm Password
                </label>
                <input
                  name="confirmPassword"
                  id="confirmPassword"
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    formErrors.confirmPassword ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Confirm your password"
                />
                {formErrors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.confirmPassword}</p>
                )}
              </div>

              {/* Error Message from Auth Hook */}
              {registerError ? (
                <div className="text-sm text-red-600 text-center">
                  {String(registerError)}
                </div>
              ) : null}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary btn-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </button>

              {/* Login Link */}
              <div className="text-center">
                <p className="text-sm text-neutral-600">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                    Sign in here
                  </Link>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
