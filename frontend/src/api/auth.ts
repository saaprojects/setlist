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
  private readonly baseUrl = '/api/v1/auth'

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post(`${this.baseUrl}/login`, credentials)
    return response.data
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post(`${this.baseUrl}/register`, userData)
    return response.data
  }

  async logout(): Promise<void> {
    await apiClient.post(`${this.baseUrl}/logout`)
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get(`${this.baseUrl}/me`)
    return response.data
  }

  async refreshToken(): Promise<AuthResponse> {
    const response = await apiClient.post(`${this.baseUrl}/refresh`)
    return response.data
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await apiClient.post(`${this.baseUrl}/password-reset`, data)
  }

  async resetPassword(data: PasswordReset): Promise<void> {
    await apiClient.post(`${this.baseUrl}/password-reset/confirm`, data)
  }

  async verifyEmail(data: EmailVerification): Promise<void> {
    await apiClient.post(`${this.baseUrl}/verify-email`, data)
  }

  async resendVerificationEmail(): Promise<void> {
    await apiClient.post(`${this.baseUrl}/resend-verification`)
  }

  async updateProfile(userId: string, data: Partial<User>): Promise<User> {
    const response = await apiClient.put(`/api/v1/users/${userId}`, data)
    return response.data
  }

  async changePassword(userId: string, currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.put(`/api/v1/users/${userId}/password`, {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  async deleteAccount(userId: string, password: string): Promise<void> {
    await apiClient.delete(`/api/v1/users/${userId}`, {
      data: { password },
    })
  }
}

export const authApi = new AuthApi()
