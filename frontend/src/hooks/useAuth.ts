import { useState, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { authApi } from '@/api/auth'
import { User } from '@/types/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  })

  const queryClient = useQueryClient()

  // Check if user is authenticated on mount
  const { data: user, isLoading: isCheckingAuth } = useQuery(
    'auth-user',
    authApi.getCurrentUser,
    {
      retry: false,
      onSuccess: (userData) => {
        setAuthState({
          user: userData,
          isAuthenticated: true,
          isLoading: false,
        })
      },
      onError: () => {
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },
    }
  )

  // Login mutation
  const loginMutation = useMutation(authApi.login, {
    onSuccess: (userData) => {
      setAuthState({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
      })
      queryClient.invalidateQueries('auth-user')
    },
    onError: (error) => {
      console.error('Login failed:', error)
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
      }))
    },
  })

  // Register mutation
  const registerMutation = useMutation(authApi.register, {
    onSuccess: (userData) => {
      setAuthState({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
      })
      queryClient.invalidateQueries('auth-user')
    },
    onError: (error) => {
      console.error('Registration failed:', error)
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
      }))
    },
  })

  // Logout mutation
  const logoutMutation = useMutation(authApi.logout, {
    onSuccess: () => {
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      })
      queryClient.clear()
    },
    onError: (error) => {
      console.error('Logout failed:', error)
      // Force logout even if API call fails
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      })
      queryClient.clear()
    },
  })

  // Login function
  const login = useCallback(async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true }))
    return loginMutation.mutateAsync({ email, password })
  }, [loginMutation])

  // Register function
  const register = useCallback(async (userData: {
    email: string
    username: string
    password: string
    display_name: string
    role: string
  }) => {
    setAuthState(prev => ({ ...prev, isLoading: true }))
    return registerMutation.mutateAsync(userData)
  }, [registerMutation])

  // Logout function
  const logout = useCallback(async () => {
    setAuthState(prev => ({ ...prev, isLoading: true }))
    return logoutMutation.mutateAsync()
  }, [logoutMutation])

  // Update loading state when auth check completes
  useEffect(() => {
    if (!isCheckingAuth) {
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
      }))
    }
  }, [isCheckingAuth])

  return {
    ...authState,
    login,
    register,
    logout,
    isLoggingIn: loginMutation.isLoading,
    isRegistering: registerMutation.isLoading,
    isLoggingOut: logoutMutation.isLoading,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
    logoutError: logoutMutation.error,
  }
}
