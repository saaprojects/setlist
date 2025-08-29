import React from 'react'
import { Link } from 'react-router-dom'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-primary-500">404</h1>
          <h2 className="text-2xl font-semibold text-neutral-900 mb-4">
            Page Not Found
          </h2>
          <p className="text-neutral-600 mb-8">
            Sorry, we couldn't find the page you're looking for. 
            It might have been moved, deleted, or you entered the wrong URL.
          </p>
        </div>
        
        <div className="space-y-4">
          <Link
            to="/"
            className="btn-primary btn-lg w-full"
          >
            Go Home
          </Link>
          <Link
            to="/shows"
            className="btn-outline btn-lg w-full"
          >
            Browse Shows
          </Link>
        </div>
      </div>
    </div>
  )
}
