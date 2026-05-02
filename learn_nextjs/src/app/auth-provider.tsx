'use client'

import { createContext, useCallback, useEffect, useReducer } from 'react'

import { UserSchema } from '@/common/schemas/api/resources'
import type { User } from '@/common/types/api/resources'
import type { Children } from '@/common/types/layout'

import { getMe } from './api/endpoints'

type AuthState =
  | { status: 'loading' }
  | { status: 'authenticated'; user: User }
  | { status: 'unauthenticated' }

interface AuthContextValue {
  state: AuthState
  onLoginSuccess: (user: User) => void
  onLogoutSuccess: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export const AuthProvider = ({ children }: Children) => {
  const [state, setAuthState] = useReducer(
    (_: AuthState, next: AuthState) => next,
    { status: 'loading' } as AuthState
  )

  const checkAuth = useCallback(async (): Promise<AuthState> => {
    const { data, error } = await getMe()

    if (!data || error) {
      return { status: 'unauthenticated' }
    }

    const user = UserSchema.safeParse(data)
    if (!user.success) {
      console.error(`Invalid user data format: ${user.error.message}`)
      return { status: 'unauthenticated' }
    }

    return { status: 'authenticated', user: user.data }
  }, [])

  const tryCheckAuth = useCallback(() => {
    checkAuth()
      .then((authState) => {
        setAuthState(authState)
      })
      .catch((error) => {
        console.error(
          `Authentication check failed: ${error ?? 'Unknown error'}`
        )
        setAuthState({ status: 'unauthenticated' })
      })
  }, [checkAuth])

  useEffect(() => {
    tryCheckAuth()

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        tryCheckAuth()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [tryCheckAuth])

  const onLoginSuccess = (user: User) => {
    setAuthState({ status: 'authenticated', user })
  }

  const onLogoutSuccess = () => {
    setAuthState({ status: 'unauthenticated' })
  }

  return (
    <AuthContext.Provider value={{ state, onLoginSuccess, onLogoutSuccess }}>
      {children}
    </AuthContext.Provider>
  )
}
