export interface User {
  id: string
  email: string
  username: string
  display_name: string
  role: UserRole
  bio?: string
  avatar_url?: string
  location?: string
  website?: string
  social_links: Record<string, string>
  is_verified: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserProfile extends User {
  // Additional profile fields
  band_name?: string
  genres?: string[]
  instruments?: string[]
  experience_years?: number
  influences?: string[]
  achievements?: string[]
  
  // Venue specific fields
  venue_name?: string
  capacity?: number
  address?: string
  city?: string
  state?: string
  country?: string
  venue_type?: string
  amenities?: string[]
  
  // Promoter specific fields
  company_name?: string
  specializations?: string[]
  past_events?: string[]
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  display_name: string
  role: UserRole
}

export interface AuthResponse {
  user: User
  access_token: string
  token_type: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordReset {
  token: string
  new_password: string
}

export interface EmailVerification {
  token: string
}

export enum UserRole {
  ARTIST = 'artist',
  PROMOTER = 'promoter',
  VENUE = 'venue',
  USER = 'user',
  ADMIN = 'admin',
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (data: Partial<UserProfile>) => Promise<void>
  resetPassword: (data: PasswordResetRequest) => Promise<void>
  verifyEmail: (data: EmailVerification) => Promise<void>
}
