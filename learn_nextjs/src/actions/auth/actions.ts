'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { getSafeNextPath } from '@/app/(auth)/getSafeNextPath'
import { API_BASE_URL } from '@/common/const'
import {
  TokenV2Schema,
  UserCreateSchema
} from '@/common/schemas/api/resources'
import { AuthActionState } from '@/types/auth/types'

export const loginAction = async (
  _prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> => {
  const email = formData.get('email')
  const password = formData.get('password')
  const rawRedirect = formData.get('redirectPath')
  const redirectPath = getSafeNextPath(
    typeof rawRedirect === 'string' ? rawRedirect : undefined
  )

  const parsed = UserCreateSchema.safeParse({ email, password })
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? 'Invalid input' }
  }

  const body = new URLSearchParams()
  body.set('username', parsed.data.email)
  body.set('password', parsed.data.password)

  const res = await fetch(`${API_BASE_URL}/v2/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  })

  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`
    try {
      const data = (await res.json()) as { detail?: unknown }
      if (typeof data.detail === 'string') message = data.detail
    } catch {}
    return { error: message }
  }

  const rawData: unknown = await res.json()
  const tokenResult = TokenV2Schema.safeParse(rawData)
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
  const email = formData.get('email')
  const password = formData.get('password')
  const rawRedirect = formData.get('redirectPath')
  const redirectPath = getSafeNextPath(
    typeof rawRedirect === 'string' ? rawRedirect : undefined
  )

  const parsed = UserCreateSchema.safeParse({ email, password })
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? 'Invalid input' }
  }

  const res = await fetch(`${API_BASE_URL}/v2/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: parsed.data.email,
      password: parsed.data.password
    })
  })

  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`
    try {
      const data = (await res.json()) as { detail?: unknown }
      if (typeof data.detail === 'string') message = data.detail
    } catch {}
    return { error: message }
  }

  redirect(redirectPath)
}

export const logoutAction = async () => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value

  if (accessToken) {
    await fetch(`${API_BASE_URL}/latest/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` }
    }).catch(() => {})
  }

  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  redirect('/login')
}
