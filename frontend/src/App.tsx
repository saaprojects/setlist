import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { HomePage } from '@/pages/HomePage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ShowsPage } from '@/pages/ShowsPage'
import { ArtistsPage } from '@/pages/ArtistsPage'
import { VenuesPage } from '@/pages/VenuesPage'
import { MusicPage } from '@/pages/MusicPage'
import { PlaylistsPage } from '@/pages/PlaylistsPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { NotFoundPage } from '@/pages/NotFoundPage'

function App() {
  return (
    <Layout>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/shows" element={<ShowsPage />} />
        <Route path="/artists" element={<ArtistsPage />} />
        <Route path="/venues" element={<VenuesPage />} />
        <Route path="/music" element={<MusicPage />} />
        <Route path="/playlists" element={<PlaylistsPage />} />
        
        {/* Protected routes */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        
        {/* 404 route */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  )
}

export default App
