'use client'

import { Children } from '@/common/types'
import { createContext, useCallback, useEffect, useReducer } from 'react'
import { User } from './api/types'
import { getMe } from './api/endpoints'
import { UserSchema } from './api/schemas'

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
      // console.error(`Failed to fetch user data: ${error ?? 'Unknown error'}`)
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
    // eslint-disable-next-line @eslint-react/no-context-provider
    <AuthContext.Provider value={{ state, onLoginSuccess, onLogoutSuccess }}>
      {children}
    </AuthContext.Provider>
  )
}
