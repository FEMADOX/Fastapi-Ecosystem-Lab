import type { User } from '@/common/types/api/resources'

export type AuthState =
  | { status: 'loading' }
  | { status: 'authenticated'; user: User }
  | { status: 'unauthenticated' }

export interface AuthContextValue {
  state: AuthState
  onLoginSuccess: (user: User) => void
  onLogoutSuccess: () => void
}

export type ResolveAuthResult = {
  authState: AuthState
  didRefresh: boolean
}
