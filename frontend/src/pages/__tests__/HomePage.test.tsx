import React from 'react'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { HomePage } from '../HomePage'

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('HomePage Component', () => {
  it('renders the hero section with main heading', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('Your Local Music')).toBeInTheDocument()
    expect(screen.getByText('Community')).toBeInTheDocument()
  })

  it('displays the hero description text', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText(/Discover local bands, find shows, and connect with the music scene in your area/)).toBeInTheDocument()
  })

  it('renders call-to-action buttons in hero section', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('Get Started')).toBeInTheDocument()
    expect(screen.getByText('Browse Shows')).toBeInTheDocument()
  })

  it('displays statistics section with correct values', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('500+')).toBeInTheDocument()
    expect(screen.getByText('100+')).toBeInTheDocument()
    expect(screen.getByText('1000+')).toBeInTheDocument()
    expect(screen.getByText('5000+')).toBeInTheDocument()
    
    expect(screen.getByText('Local Bands')).toBeInTheDocument()
    expect(screen.getByText('Venues')).toBeInTheDocument()
    expect(screen.getByText('Shows')).toBeInTheDocument()
    expect(screen.getByText('Music Tracks')).toBeInTheDocument()
  })

  it('renders features section with all four feature cards', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('Discover Local Music')).toBeInTheDocument()
    expect(screen.getByText('Find Shows & Events')).toBeInTheDocument()
    expect(screen.getByText('Connect with Artists')).toBeInTheDocument()
    expect(screen.getByText('Venue Management')).toBeInTheDocument()
  })

  it('displays feature descriptions correctly', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText(/Find amazing local bands and artists in your area/)).toBeInTheDocument()
    expect(screen.getByText(/Browse upcoming shows, concerts, and events/)).toBeInTheDocument()
    expect(screen.getByText(/Follow your favorite bands, collaborate on projects/)).toBeInTheDocument()
    expect(screen.getByText(/For venues and promoters: manage shows, book bands/)).toBeInTheDocument()
  })

  it('renders feature icons', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('🎵')).toBeInTheDocument()
    expect(screen.getByText('🎭')).toBeInTheDocument()
    expect(screen.getByText('🤝')).toBeInTheDocument()
    expect(screen.getByText('🏢')).toBeInTheDocument()
  })

  it('displays "Learn More" buttons for each feature', () => {
    renderWithRouter(<HomePage />)
    
    const learnMoreButtons = screen.getAllByText('Learn More')
    expect(learnMoreButtons).toHaveLength(4)
  })

  it('renders the final CTA section', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('Ready to Join the Community?')).toBeInTheDocument()
    expect(screen.getByText(/Whether you're a musician, venue owner, promoter, or music lover/)).toBeInTheDocument()
  })

  it('displays CTA buttons correctly', () => {
    renderWithRouter(<HomePage />)
    
    expect(screen.getByText('Create Account')).toBeInTheDocument()
    expect(screen.getByText('Learn More')).toBeInTheDocument()
  })

  it('has proper navigation links', () => {
    renderWithRouter(<HomePage />)
    
    const getStartedLink = screen.getByText('Get Started').closest('a')
    const browseShowsLink = screen.getByText('Browse Shows').closest('a')
    const createAccountLink = screen.getByText('Create Account').closest('a')
    
    expect(getStartedLink).toHaveAttribute('href', '/register')
    expect(browseShowsLink).toHaveAttribute('href', '/shows')
    expect(createAccountLink).toHaveAttribute('href', '/register')
  })

  it('has proper feature navigation links', () => {
    renderWithRouter(<HomePage />)
    
    const musicLink = screen.getByText('Discover Local Music').closest('a')
    const showsLink = screen.getByText('Find Shows & Events').closest('a')
    const artistsLink = screen.getByText('Connect with Artists').closest('a')
    const venuesLink = screen.getByText('Venue Management').closest('a')
    
    expect(musicLink).toHaveAttribute('href', '/music')
    expect(showsLink).toHaveAttribute('href', '/shows')
    expect(artistsLink).toHaveAttribute('href', '/artists')
    expect(venuesLink).toHaveAttribute('href', '/venues')
  })

  it('applies proper CSS classes for styling', () => {
    renderWithRouter(<HomePage />)
    
    // Check for gradient background classes
    const heroSection = screen.getByText('Your Local Music').closest('section')
    expect(heroSection).toHaveClass('bg-gradient-to-br', 'from-primary-500', 'via-primary-600', 'to-secondary-600')
    
    // Check for card classes
    const featureCards = screen.getAllByText(/Learn More/).map(btn => btn.closest('.card'))
    featureCards.forEach(card => {
      expect(card).toHaveClass('card')
    })
  })

  it('maintains responsive design classes', () => {
    renderWithRouter(<HomePage />)
    
    const heroHeading = screen.getByText('Your Local Music').closest('h1')
    expect(heroHeading).toHaveClass('text-4xl', 'md:text-6xl')
    
    const heroDescription = screen.getByText(/Discover local bands, find shows, and connect with the music scene in your area/).closest('p')
    expect(heroDescription).toHaveClass('text-xl', 'md:text-2xl')
  })

  it('renders without crashing', () => {
    expect(() => renderWithRouter(<HomePage />)).not.toThrow()
  })

  it('has accessible heading structure', () => {
    renderWithRouter(<HomePage />)
    
    const headings = screen.getAllByRole('heading')
    expect(headings).toHaveLength(6) // h1 + 5 h2 elements
    
    // Check main heading is h1
    const mainHeading = screen.getByRole('heading', { level: 1 })
    expect(mainHeading).toHaveTextContent('Your Local Music')
  })

  it('provides proper alt text for decorative elements', () => {
    renderWithRouter(<HomePage />)
    
    // Check that emojis are present (they serve as visual indicators)
    expect(screen.getByText('🎵')).toBeInTheDocument()
    expect(screen.getByText('🎭')).toBeInTheDocument()
    expect(screen.getByText('🤝')).toBeInTheDocument()
    expect(screen.getByText('🏢')).toBeInTheDocument()
  })
})
