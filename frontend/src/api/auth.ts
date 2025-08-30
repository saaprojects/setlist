import { apiClient } from './client'
import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  User,
  PasswordResetRequest,
  PasswordReset,
  EmailVerification,
} from '@/types/auth'

class AuthApi {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new FormData()
    formData.append('username', credentials.email) // Backend now supports both username and email
    formData.append('password', credentials.password)
    
    const response = await apiClient.post('http://localhost:8000/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post('http://localhost:8000/api/v1/auth/register', userData)
    return response.data
  }

  async logout(): Promise<void> {
    await apiClient.post('http://localhost:8000/api/v1/auth/logout')
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('http://localhost:8000/api/v1/auth/me')
    return response.data
  }

  async refreshToken(): Promise<AuthResponse> {
    const response = await apiClient.post('http://localhost:8000/api/v1/auth/refresh')
    return response.data
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await apiClient.post('http://localhost:8000/api/v1/auth/password-reset', data)
  }

  async resetPassword(data: PasswordReset): Promise<void> {
    await apiClient.post('http://localhost:8000/api/v1/auth/password-reset/confirm', data)
  }

  async verifyEmail(data: EmailVerification): Promise<void> {
    await apiClient.post('http://localhost:8000/api/v1/auth/verify-email', data)
  }

  async resendVerificationEmail(): Promise<void> {
    await apiClient.post('http://localhost:8000/api/v1/auth/resend-verification')
  }

  async updateProfile(userId: string, data: Partial<User>): Promise<User> {
    const response = await apiClient.put(`http://localhost:8000/api/v1/users/${userId}`, data)
    return response.data
  }

  async changePassword(userId: string, currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.put(`http://localhost:8000/api/v1/users/${userId}/password`, {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  async deleteAccount(userId: string, password: string): Promise<void> {
    await apiClient.delete(`http://localhost:8000/api/v1/users/${userId}`, {
      data: { password },
    })
  }
}

export const authApi = new AuthApi()
