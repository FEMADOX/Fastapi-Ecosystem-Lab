import { UserSchema } from '@/common/schemas/api/resources'
import type { User } from '@/common/types/api/resources'
import { getMe, refreshAccessToken } from './api/endpoints'
import type { AuthState } from './auth-provider.types'

export const toAuthenticatedState = (rawUser: User): AuthState => {
  const user = UserSchema.safeParse(rawUser)

  if (!user.success) {
    throw new Error(`Invalid user data format: ${user.error.message}`)
  }

  return { status: 'authenticated', user: user.data }
}

export const getCsrfTokenFromCookies = (): string | null => {
  const csrfToken = document.cookie
    .split('; ')
    .find((cookie) => cookie.startsWith('csrf_token='))
    ?.slice('csrf_token='.length)

  return csrfToken ? decodeURIComponent(csrfToken) : null
}

const getCurrentUserState = async (): Promise<AuthState | null> => {
  const currentUserResult = await getMe()

  if (!currentUserResult.data || currentUserResult.error) {
    return null
  }

  return toAuthenticatedState(currentUserResult.data)
}

export const attemptRefresh = async (): Promise<boolean> => {
  const csrfToken = getCsrfTokenFromCookies()

  if (!csrfToken) {
    return false
  }

  const refreshResult = await refreshAccessToken(csrfToken)

  return !refreshResult.error && refreshResult.data?.refreshed === true
}

export const resolveAuthState = async (): Promise<AuthState> => {
  const currentUserState = await getCurrentUserState()

  if (currentUserState) {
    return currentUserState
  }

  const refreshed = await attemptRefresh()

  if (!refreshed) {
    return { status: 'unauthenticated' }
  }

  return (await getCurrentUserState()) ?? { status: 'unauthenticated' }
}
