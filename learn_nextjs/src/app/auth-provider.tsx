'use client'

import { useRouter } from 'next/navigation'
import { createContext, useCallback, useEffect, useReducer } from 'react'
import { toast } from 'sonner'
import type { User } from '@/common/types/api/resources'
import type { Children } from '@/common/types/layout'
import { resolveAuthState } from './auth-provider.helpers'
import type {
  AuthContextValue,
  AuthState,
  ResolveAuthResult
} from './auth-provider.types'
import {
  SSEGlobalNotifications,
  SSEUserNotifications
} from './components/notifications/toasts'

export const AuthContext = createContext<AuthContextValue | null>(null)

export const AuthProvider = ({ children }: Children) => {
  const [state, setAuthState] = useReducer(
    (_: AuthState, next: AuthState) => next,
    { status: 'loading' } as AuthState
  )
  const router = useRouter()

  const checkAuth = useCallback(async (): Promise<ResolveAuthResult> => {
    return resolveAuthState()
  }, [])

  const tryCheckAuth = useCallback(() => {
    checkAuth()
      .then(({ authState, didRefresh }) => {
        setAuthState(authState)
        if (didRefresh && authState.status === 'authenticated') {
          router.refresh()
        }
      })
      .catch((error) => {
        const message =
          error instanceof Error ? error.message : 'Authentication failed.'
        toast.error(message)
        setAuthState({ status: 'unauthenticated' })
      })
  }, [checkAuth, router])

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
      <SSEGlobalNotifications />
      <SSEUserNotifications />
      {children}
    </AuthContext.Provider>
  )
}
