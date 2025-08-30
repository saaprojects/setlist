import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

interface LoginFormData {
  email: string
  password: string
}

export const LoginPage: React.FC = () => {
  const { login, isLoading, loginError } = useAuth()
  const [formErrors, setFormErrors] = useState<Partial<LoginFormData>>({})
  
  const validateForm = () => {
    const newErrors: Partial<LoginFormData> = {}
    
    // Get current form values
    const emailInput = document.getElementById('email') as HTMLInputElement
    const passwordInput = document.getElementById('password') as HTMLInputElement
    
    const email = emailInput?.value || ''
    const password = passwordInput?.value || ''
    
    if (!email) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address'
    }
    
    if (!password) {
      newErrors.password = 'Password is required'
    }
    
    setFormErrors(newErrors)
    return newErrors
  }
  
  const onSubmit = async (data: LoginFormData) => {
    const errors = validateForm()
    
    if (Object.keys(errors).length > 0) {
      return
    }
    
    try {
      await login(data.email, data.password)
    } catch (err) {
      // Error handling is done by the useAuth hook
    }
  }

  // Handle form submission
  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const email = formData.get('email') as string
    const password = formData.get('password') as string
    
    onSubmit({ email, password })
  }
  
  // Handle button click to show validation errors
  const handleButtonClick = () => {
    validateForm()
  }



  const displayErrors = formErrors

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-neutral-900">Login to Setlist</h2>
          <p className="mt-2 text-sm text-neutral-600">
            Welcome back! Please sign in to your account.
          </p>
        </div>
        
        <div className="card">
          <div className="card-content">
            <form onSubmit={handleFormSubmit} className="space-y-6" role="form">
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
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    displayErrors.email ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Enter your email"
                />
                {displayErrors.email && (
                  <p className="mt-1 text-sm text-red-600">{displayErrors.email}</p>
                )}
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
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                    displayErrors.password ? 'border-red-300' : 'border-neutral-300'
                  }`}
                  placeholder="Enter your password"
                />
                {displayErrors.password && (
                  <p className="mt-1 text-sm text-red-600">{displayErrors.password}</p>
                )}
              </div>

              {/* Error Message from Auth Hook */}
              {loginError ? (
                <div className="text-sm text-red-600 text-center">
                  {String(loginError)}
                </div>
              ) : null}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                onClick={handleButtonClick}
                className="w-full btn-primary btn-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing In...' : 'Sign In'}
              </button>
            </form>

            {/* Navigation Links */}
            <div className="mt-6 text-center space-y-2">
              <p className="text-sm text-neutral-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-primary-600 hover:text-primary-500 font-medium">
                  Sign up
                </Link>
              </p>
              <p className="text-sm">
                <Link to="/forgot-password" className="text-primary-600 hover:text-primary-500">
                  Forgot your password?
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
