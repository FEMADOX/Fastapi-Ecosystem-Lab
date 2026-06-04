'use server'

import { cookies } from 'next/headers'
import { getSafeNextPath } from '@/app/(auth)/getSafeNextPath'
import { login, logout, signup } from '@/app/api/server-endpoints'
import { TokenV2Schema, UserCreateSchema } from '@/common/schemas/api/resources'
import type { AuthActionState } from '@/types/auth/types'

const baseAuthAction = async (formData: FormData) => {
  const email = formData.get('email')
  const password = formData.get('password')
  const rawRedirect = formData.get('redirectPath')
  const redirectPath = getSafeNextPath(
    typeof rawRedirect === 'string' ? rawRedirect : undefined
  )
  const data = { email, password }

  const parsed = UserCreateSchema.safeParse(data)
  if (!parsed.success) {
    return {
      success: false,
      error: parsed.error.issues[0]?.message ?? 'Invalid input'
    }
  }

  return { success: true, parsed: parsed.data, redirectPath }
}

export const loginAction = async (
  _prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> => {
  const baseResult = await baseAuthAction(formData)

  if (!baseResult.success || !baseResult.parsed || !baseResult.redirectPath) {
    return { error: baseResult.error ?? `Failed to process auth data` }
  }

  const body = new URLSearchParams()

  const { email, password } = baseResult.parsed
  body.set('username', email)
  body.set('password', password)

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
    refresh_expires_in: refreshExpiresIn,
    csrf_token: csrfToken
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
  cookieStore.set('csrf_token', csrfToken, {
    httpOnly: false,
    sameSite: 'lax',
    path: '/',
    expires: new Date(Date.now() + refreshExpiresIn * 1000),
    secure: isProduction
  })

  return { success: true, redirectTo: baseResult.redirectPath }
}

export const registerAction = async (
  _prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> => {
  const baseResult = await baseAuthAction(formData)

  if (!baseResult.success || !baseResult.parsed || !baseResult.redirectPath) {
    return { error: baseResult.error ?? `Failed to process auth data` }
  }

  const response = await signup(baseResult.parsed)

  if (!response.data || response.error) {
    return {
      error: `Registration failed. ${response.error ?? 'Unknown error'}.`
    }
  }

  return { success: true, redirectTo: baseResult.redirectPath }
}

export const logoutAction = async () => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value

  if (accessToken) await logout(accessToken)

  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')

  return { success: true }
}
