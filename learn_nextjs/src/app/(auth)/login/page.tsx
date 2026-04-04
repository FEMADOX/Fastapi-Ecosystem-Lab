'use client'

import { login } from '@/app/api/endpoints'
import { AuthForm } from '../AuthForm'
import { loginFormSchema } from '../schema'
import { useSafeNext } from '../useSafeNext'
// import { Suspense } from 'react'

const LoginPage = () => {
  const redirectPath = useSafeNext()
  return (
    <AuthForm
      title="Login"
      submitLabel="Sign in"
      submittingLabel="Signing in..."
      schema={loginFormSchema}
      actionApi={login}
      redirectPath={redirectPath}
    />
  )
}

// const LoginPage = () => (
//   <Suspense>
//     <LoginContent />
//   </Suspense>
// )

export default LoginPage
