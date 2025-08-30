import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { LoginPage } from '../LoginPage'

// Mock the useAuth hook
const mockUseAuth = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: jest.fn(),
  error: null,
  loginError: null as string | null,
}

jest.mock('@/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth,
}))

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('LoginPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders login form elements', () => {
    renderWithProviders(<LoginPage />)
    
    expect(screen.getByText('Login to Setlist')).toBeInTheDocument()
    expect(screen.getByText('Welcome back! Please sign in to your account.')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument()
  })

  it('displays form validation errors for empty fields', async () => {
    renderWithProviders(<LoginPage />)
    
    const signInButton = screen.getByRole('button', { name: 'Sign In' })
    fireEvent.click(signInButton)
    
    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument()
      expect(screen.getByText('Password is required')).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    renderWithProviders(<LoginPage />)
    
    const emailInput = screen.getByLabelText('Email')
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
    
    const signInButton = screen.getByRole('button', { name: 'Sign In' })
    fireEvent.click(signInButton)
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument()
    })
  })

  it('calls login function with valid credentials', async () => {
    renderWithProviders(<LoginPage />)
    
    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const signInButton = screen.getByRole('button', { name: 'Sign In' })
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(signInButton)
    
    await waitFor(() => {
      expect(mockUseAuth.login).toHaveBeenCalledWith('test@example.com', 'password123')
    })
  })

  it('shows loading state during login', () => {
    mockUseAuth.isLoading = true
    renderWithProviders(<LoginPage />)
    
    const signInButton = screen.getByRole('button', { name: 'Signing In...' })
    expect(signInButton).toBeDisabled()
    expect(signInButton).toHaveTextContent('Signing In...')
  })

  it('displays error message from auth hook', () => {
    mockUseAuth.loginError = 'Invalid credentials'
    renderWithProviders(<LoginPage />)
    
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
  })

  it('has proper navigation links', () => {
    renderWithProviders(<LoginPage />)
    
    expect(screen.getByText("Don't have an account?")).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Sign up' })).toHaveAttribute('href', '/register')
    expect(screen.getByRole('link', { name: 'Forgot your password?' })).toHaveAttribute('href', '/forgot-password')
  })

  it('applies proper CSS classes for styling', () => {
    renderWithProviders(<LoginPage />)
    
    // Find the main container div that has the min-h-screen classes
    const mainContainer = screen.getByText('Login to Setlist').closest('div[class*="min-h-screen"]')
    expect(mainContainer).toHaveClass('min-h-screen', 'flex', 'items-center', 'justify-center', 'bg-neutral-50')
    
    const form = screen.getByRole('form')
    expect(form).toHaveClass('space-y-6')
  })

  it('maintains responsive design classes', () => {
    renderWithProviders(<LoginPage />)
    
    // Find the main container div that has the responsive classes
    const mainContainer = screen.getByText('Login to Setlist').closest('div[class*="min-h-screen"]')
    expect(mainContainer).toHaveClass('py-12', 'px-4', 'sm:px-6', 'lg:px-8')
    
    const formContainer = screen.getByRole('form').closest('div')
    expect(formContainer).toHaveClass('card-content')
  })

  it('renders without crashing', () => {
    expect(() => renderWithProviders(<LoginPage />)).not.toThrow()
  })

  it('has accessible form structure', () => {
    renderWithProviders(<LoginPage />)
    
    const form = screen.getByRole('form')
    expect(form).toBeInTheDocument()
    
    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    
    expect(emailInput).toHaveAttribute('type', 'email')
    expect(passwordInput).toHaveAttribute('type', 'password')
    expect(emailInput).toHaveAttribute('required')
    expect(passwordInput).toHaveAttribute('required')
  })
})
