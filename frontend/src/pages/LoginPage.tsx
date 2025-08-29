import React from 'react'

export const LoginPage: React.FC = () => {
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
            <p className="text-center text-neutral-500">
              Login form coming soon...
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
