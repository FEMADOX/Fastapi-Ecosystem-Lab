'use client'

import { createContext, useCallback, useEffect, useReducer } from 'react'
import { toast } from 'sonner'
import { UserSchema } from '@/common/schemas/api/resources'
import type { User } from '@/common/types/api/resources'
import type { Children } from '@/common/types/layout'
import { getMe, refreshAccessToken } from './api/endpoints'

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
    const toAuthenticatedState = (rawUser: User): AuthState => {
      const user = UserSchema.safeParse(rawUser)
      if (!user.success) {
        throw new Error(`Invalid user data format: ${user.error.message}`)
      }
      return { status: 'authenticated', user: user.data }
    }

    const currentUserResult = await getMe()
    if (currentUserResult.data && !currentUserResult.error) {
      return toAuthenticatedState(currentUserResult.data)
    }

    const csrfToken = document.cookie
      .split('; ')
      .find((cookie) => cookie.startsWith('csrf_token='))
      ?.split('=')[1]

    if (!csrfToken) return { status: 'unauthenticated' }

    const refreshResult = await refreshAccessToken(csrfToken)

    if (refreshResult.error || refreshResult.data?.refreshed !== true) {
      return { status: 'unauthenticated' }
    }

    const retriedUserResult = await getMe()
    if (!retriedUserResult.data || retriedUserResult.error) {
      return { status: 'unauthenticated' }
    }

    return toAuthenticatedState(retriedUserResult.data)
  }, [])

  const tryCheckAuth = useCallback(() => {
    checkAuth()
      .then((authState) => {
        setAuthState(authState)
      })
      .catch((error) => {
        const message =
          error instanceof Error ? error.message : 'Authentication failed.'
        toast.error(message)
        setAuthState({ status: 'unauthenticated' })
      })
  }, [checkAuth])

  useEffect(() => {
    tryCheckAuth()
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
