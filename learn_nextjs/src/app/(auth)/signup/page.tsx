'use client'

import { register } from '@/app/api/endpoints'
import { registerFormSchema } from '../schema'
import { AuthForm } from '../AuthForm'

const SignUpPage = () => (
  <AuthForm
    title="Sign Up"
    submitLabel="Sign up"
    submittingLabel="Signing up..."
    schema={registerFormSchema}
    actionApi={register}
    redirectPath="/login"
  />
)

export default SignUpPage
