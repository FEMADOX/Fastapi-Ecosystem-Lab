'use client'

import { login } from '@/app/api/endpoints'
import { loginFormSchema } from '../schema'
import { AuthForm } from '../AuthForm'

const LoginPage = () => (
  <AuthForm
    title="Login"
    submitLabel="Sign in"
    submittingLabel="Signing in..."
    schema={loginFormSchema}
    actionApi={login}
    redirectPath="/"
  />
)

export default LoginPage
