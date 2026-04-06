import { registerAction } from '@/actions/auth/actions'
import type { AuthPageProps } from '@/types/auth/types'

import { AuthForm } from '../AuthForm'
import { getSafeNextPath } from '../getSafeNextPath'

const SignUpPage = async ({ searchParams }: AuthPageProps) => {
  const { next } = await searchParams
  const safeNext = getSafeNextPath(next)
  const redirectPath = `/login?next=${encodeURIComponent(safeNext)}`

  return (
    <AuthForm
      title="Sign Up"
      submitLabel="Sign up"
      submittingLabel="Signing up..."
      action={registerAction}
      redirectPath={redirectPath}
    />
  )
}

export default SignUpPage
