import React from 'react'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Layout } from '../Layout'

// Mock the child components
jest.mock('@/components/Header', () => ({
  Header: () => <div data-testid="header">Header</div>,
}))

jest.mock('@/components/Footer', () => ({
  Footer: () => <div data-testid="footer">Footer</div>,
}))

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Layout Component', () => {
  it('renders header, main content, and footer', () => {
    renderWithRouter(
      <Layout>
        <div data-testid="main-content">Main Content</div>
      </Layout>
    )

    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('main-content')).toBeInTheDocument()
    expect(screen.getByTestId('footer')).toBeInTheDocument()
  })

  it('renders children content in main section', () => {
    const testContent = 'Test content for layout'
    
    renderWithRouter(
      <Layout>
        <div>{testContent}</div>
      </Layout>
    )

    expect(screen.getByText(testContent)).toBeInTheDocument()
  })

  it('applies proper CSS classes for layout structure', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    const mainElement = screen.getByRole('main')
    expect(mainElement).toHaveClass('min-h-screen', 'flex', 'flex-col')
  })

  it('renders without crashing when no children provided', () => {
    renderWithRouter(<Layout />)
    
    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('footer')).toBeInTheDocument()
  })

  it('maintains proper semantic HTML structure', () => {
    renderWithRouter(
      <Layout>
        <h1>Page Title</h1>
      </Layout>
    )

    const mainElement = screen.getByRole('main')
    expect(mainElement).toBeInTheDocument()
    expect(mainElement.tagName).toBe('MAIN')
  })
})
