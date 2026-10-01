import { useState, useEffect, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import api, { saveJwtTokens, clearJwtTokens, hasJwtTokens } from '../api/client'
import { AuthContext } from './authContext'

export function AuthProvider({ children }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(hasJwtTokens())

  
  useEffect(() => {
    // On mount, fetch the current user if we have tokens
    if (hasJwtTokens()) {
      api.get('/api/v1/auth/user/')
        .then((data) => setUser(data))
        .catch(() => {
          clearJwtTokens()
          setUser(null)
        })
        .finally(() => setLoading(false))
    }
  }, [])

  const login = useCallback(async (username, password) => {
    const data = await api.post('/api/v1/auth/login/', { username, password })
    saveJwtTokens(data.access, data.refresh)
    setUser(data.user)
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.post('/api/v1/auth/logout/')
    } catch {
      // Server-side logout failed — continue with local cleanup
    }
    clearJwtTokens()
    setUser(null)
    queryClient.clear()
  }, [queryClient])

  const register = useCallback(async (username, email, password) => {
    await api.post('/api/v1/auth/register/', { username, email, password })
    await login(username, password)
  }, [login])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}
