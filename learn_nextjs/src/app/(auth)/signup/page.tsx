'use client'

import { register } from '@/app/api/endpoints'
import { registerFormSchema } from '../schema'
import { AuthForm } from '../AuthForm'
import { useSafeNext } from '../useSafeNext'
import { Suspense } from 'react'

const SignUpContent = () => {
  const safeNext = useSafeNext()
  const redirectPath = `/login?next=${encodeURIComponent(safeNext)}`
  return (
    <AuthForm
      title="Sign Up"
      submitLabel="Sign up"
      submittingLabel="Signing up..."
      schema={registerFormSchema}
      actionApi={register}
      redirectPath={redirectPath}
    />
  )
}

const SignUpPage = () => (
  <Suspense>
    <SignUpContent />
  </Suspense>
)

export default SignUpPage
