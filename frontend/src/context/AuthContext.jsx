import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  authApi,
  getApiError,
  getStoredToken,
  setStoredToken,
} from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken())
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    function handleUnauthorized() {
      setStoredToken(null)
      setToken(null)
      setUser(null)
      setLoading(false)
    }

    window.addEventListener('scholarflow:unauthorized', handleUnauthorized)
    return () => {
      window.removeEventListener('scholarflow:unauthorized', handleUnauthorized)
    }
  }, [])

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    let cancelled = false

    async function loadCurrentUser() {
      setLoading(true)
      try {
        const response = await authApi.me()
        if (!cancelled) {
          setUser(response.data)
        }
      } catch {
        if (!cancelled) {
          setStoredToken(null)
          setToken(null)
          setUser(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadCurrentUser()

    return () => {
      cancelled = true
    }
  }, [token])

  async function login(credentials) {
    try {
      const response = await authApi.login(credentials)
      const nextToken = response.data.access_token
      setStoredToken(nextToken)
      setToken(nextToken)
      const currentUser = await authApi.me()
      setUser(currentUser.data)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: getApiError(error, 'Unable to sign in'),
      }
    }
  }

  async function register(payload) {
    try {
      await authApi.register(payload)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: getApiError(error, 'Unable to create account'),
      }
    }
  }

  function logout() {
    setStoredToken(null)
    setToken(null)
    setUser(null)
  }

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token && user),
      login,
      register,
      logout,
    }),
    [token, user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
