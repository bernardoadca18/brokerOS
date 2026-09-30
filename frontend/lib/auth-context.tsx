'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { authApi, UserWithOrganizationResponse, ApiClientError } from './api'

interface AuthContextType {
  user: UserWithOrganizationResponse | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (organization: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserWithOrganizationResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Always check if user is authenticated
    authApi
      .me()
      .then((userData) => {
        setUser(userData)
        // If on login page with valid session, redirect to overview
        if (pathname === '/login') {
          router.push('/overview')
        }
      })
      .catch(() => {
        setUser(null)
        // Redirect to login if not authenticated and not already on login page
        if (pathname !== '/login') {
          router.push('/login')
        }
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [pathname, router])

  const login = async (organization: string, email: string, password: string) => {
    const response = await authApi.login({ organization, email, password })
    setUser(response.user)
    router.push('/overview')
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch {
      // Ignore logout errors
    }
    setUser(null)
    router.push('/login')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
