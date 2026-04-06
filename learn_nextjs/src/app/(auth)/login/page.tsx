import { loginAction } from '@/actions/auth/actions'
import type { AuthPageProps } from '@/types/auth/types'

import { AuthForm } from '../AuthForm'
import { getSafeNextPath } from '../getSafeNextPath'

const LoginPage = async ({ searchParams }: AuthPageProps) => {
  const { next } = await searchParams
  const redirectPath = getSafeNextPath(next)
  const AUTH_PATHS = ['/login', '/signup']
  const safeRedirectPath =
    redirectPath === '/' ||
    AUTH_PATHS.some((path) => redirectPath.startsWith(path))
      ? ''
      : redirectPath

  return (
    <AuthForm
      title="Login"
      submitLabel="Sign in"
      submittingLabel="Signing in..."
      action={loginAction}
      redirectPath={safeRedirectPath}
    />
  )
}

export default LoginPage
