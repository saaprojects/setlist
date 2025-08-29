import React from 'react'
import { Link } from 'react-router-dom'

export const HomePage: React.FC = () => {
  const features = [
    {
      title: 'Discover Local Music',
      description: 'Find amazing local bands and artists in your area. Stream their music and discover new sounds.',
      icon: '🎵',
      href: '/music',
    },
    {
      title: 'Find Shows & Events',
      description: 'Browse upcoming shows, concerts, and events. Get tickets and never miss a great performance.',
      icon: '🎭',
      href: '/shows',
    },
    {
      title: 'Connect with Artists',
      description: 'Follow your favorite bands, collaborate on projects, and build meaningful connections.',
      icon: '🤝',
      href: '/artists',
    },
    {
      title: 'Venue Management',
      description: 'For venues and promoters: manage shows, book bands, and grow your music community.',
      icon: '🏢',
      href: '/venues',
    },
  ]

  const stats = [
    { label: 'Local Bands', value: '500+' },
    { label: 'Venues', value: '100+' },
    { label: 'Shows', value: '1000+' },
    { label: 'Music Tracks', value: '5000+' },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-600 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Your Local Music
              <span className="block text-secondary-300">Community</span>
            </h1>
            <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
              Discover local bands, find shows, and connect with the music scene in your area. 
              The ultimate platform for local music lovers, artists, and venues.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="btn-secondary btn-lg text-lg px-8 py-4"
              >
                Get Started
              </Link>
              <Link
                to="/shows"
                className="btn-outline btn-lg text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-primary-600"
              >
                Browse Shows
              </Link>
            </div>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-white/10 rounded-full"></div>
        <div className="absolute bottom-20 right-20 w-32 h-32 bg-white/5 rounded-full"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-white/10 rounded-full"></div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-neutral-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-4">
              Everything You Need for Local Music
            </h2>
            <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
              Setlist provides all the tools and features you need to discover, 
              connect, and grow your local music community.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="card hover:shadow-lg transition-shadow">
                <div className="card-content text-center">
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="card-title text-lg mb-3">{feature.title}</h3>
                  <p className="text-neutral-600 mb-4">{feature.description}</p>
                  <Link
                    to={feature.href}
                    className="btn-primary btn-sm"
                  >
                    Learn More
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-neutral-800 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Join the Community?
          </h2>
          <p className="text-xl text-neutral-300 mb-8">
            Whether you're a musician, venue owner, promoter, or music lover, 
            Setlist has something for you. Start building your local music scene today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="btn-primary btn-lg text-lg"
            >
              Create Account
            </Link>
            <Link
              to="/about"
              className="btn-outline btn-lg text-lg border-white text-white hover:bg-white hover:text-neutral-800"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
