'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { getSafeNextPath } from '@/app/(auth)/getSafeNextPath'
import { login, logout, signup } from '@/app/api/server-endpoints'
import { TokenV2Schema, UserCreateSchema } from '@/common/schemas/api/resources'
import type { AuthActionState } from '@/types/auth/types'

const processAuthFormData = (formData: FormData) => {
  const email = formData.get('email')
  const password = formData.get('password')
  const rawRedirect = formData.get('redirectPath')
  const redirectPath = getSafeNextPath(
    typeof rawRedirect === 'string' ? rawRedirect : undefined
  )
  return { data: { email, password }, redirectPath }
}

export const loginAction = async (
  _prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> => {
  const { data, redirectPath } = processAuthFormData(formData)

  const parsed = UserCreateSchema.safeParse(data)
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? 'Invalid input' }
  }

  const body = new URLSearchParams()
  body.set('username', parsed.data.email)
  body.set('password', parsed.data.password)

  const response = await login(body)
  if (!response.data || response.error) {
    return { error: response.error ?? 'Login failed. Please try again.' }
  }

  const tokenResult = TokenV2Schema.safeParse(response.data)
  if (!tokenResult.success) {
    return { error: 'Invalid login response from server' }
  }

  const {
    access_token: accessToken,
    refresh_token: refreshToken,
    access_expires_in: accessExpiresIn,
    refresh_expires_in: refreshExpiresIn
  } = tokenResult.data

  const cookieStore = await cookies()
  const isProduction = process.env.ENVIRONMENT === 'production'

  cookieStore.set('access_token', accessToken, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    expires: new Date(Date.now() + accessExpiresIn * 1000),
    secure: isProduction
  })
  cookieStore.set('refresh_token', refreshToken, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    expires: new Date(Date.now() + refreshExpiresIn * 1000),
    secure: isProduction
  })

  redirect(redirectPath)
}

export const registerAction = async (
  _prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> => {
  const { data, redirectPath } = processAuthFormData(formData)

  const parsed = UserCreateSchema.safeParse(data)
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? 'Invalid input' }
  }

  const parsedData = {
    email: parsed.data.email,
    password: parsed.data.password
  }
  const response = await signup(parsedData)

  if (!response.data || response.error) {
    return {
      error: `Registration failed. ${response.error ?? 'Unknown error'}.`
    }
  }

  redirect(redirectPath)
}

export const logoutAction = async () => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value

  if (accessToken) await logout(accessToken)

  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  redirect('/login')
}
