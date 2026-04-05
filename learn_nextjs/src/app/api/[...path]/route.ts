import { cookies } from 'next/headers'
import { type NextRequest, NextResponse } from 'next/server'

import { API_BASE_URL as BACKEND_URL } from '@/common/const'
import { TokenV2Schema } from '@/common/schemas/api/resources'
import { PromisePathProps } from '@/types/api/types'

const handler = async (
  request: NextRequest,
  pathname: string
): Promise<NextResponse> => {
  const [apiVersion, ...pathParts] = pathname.split('/')
  const apiPath = pathParts.join('/')

  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value
  const refreshToken = cookieStore.get('refresh_token')?.value
  const forwardHeaders = new Headers()

  forwardHeaders.set(
    'Content-Type',
    request.headers.get('Content-Type') ?? 'application/json'
  )
  if (accessToken) {
    forwardHeaders.set('Authorization', `Bearer ${accessToken}`)
  }
  const isRefreshEndpoint = apiPath === 'auth/refresh'
  if (refreshToken && isRefreshEndpoint) {
    forwardHeaders.set('X-Refresh-Token', refreshToken)
  }

  const backendRes = await fetch(`${BACKEND_URL}/${apiVersion}/${apiPath}`, {
    method: request.method,
    headers: forwardHeaders,
    body: request.method !== 'GET' ? await request.text() : undefined
  })

  if (!backendRes.ok) {
    return new NextResponse(backendRes.body, {
      status: backendRes.status,
      headers: {
        'Content-Type':
          backendRes.headers.get('Content-Type') ?? 'application/json'
      }
    })
  }

  const isLogin = apiPath === 'auth/token'
  const isLogout = apiPath === 'auth/logout'

  if (isLogin) {
    const rawData: unknown = await backendRes.json()
    const { data, error, success } = TokenV2Schema.safeParse(rawData)
    if (!success || error) {
      return NextResponse.json(
        {
          detail: `Invalid login response: ${error?.message ?? 'Unknown error'}`
        },
        { status: 502 }
      )
    }

    const response = NextResponse.json({ loggedIn: true })

    const {
      access_token: accessToken,
      refresh_token: refreshToken,
      access_expires_in: accessExpiresIn,
      refresh_expires_in: refreshExpiresIn
    } = data
    response.cookies.set('access_token', accessToken, {
      httpOnly: true,
      sameSite: 'lax',
      path: '/',
      expires: new Date(Date.now() + accessExpiresIn * 1000),
      secure: process.env.ENVIRONMENT === 'production'
    })
    response.cookies.set('refresh_token', refreshToken, {
      httpOnly: true,
      sameSite: 'lax',
      path: '/',
      expires: new Date(Date.now() + refreshExpiresIn * 1000),
      secure: process.env.ENVIRONMENT === 'production'
    })

    return response
  }
  if (isLogout) {
    if (backendRes.status !== 204) {
      return NextResponse.json(
        { detail: 'Invalid logout response' },
        { status: 502 }
      )
    }

    const response = NextResponse.json({ loggedOut: true })
    response.cookies.delete('access_token')
    response.cookies.delete('refresh_token')
    return response
  }

  const body = await backendRes.text()
  return new NextResponse(body, {
    status: backendRes.status,
    headers: {
      'Content-Type':
        backendRes.headers.get('Content-Type') ?? 'application/json'
    }
  })
}

const methodHandler = async (
  request: NextRequest,
  { params }: PromisePathProps
) => {
  const { path } = await params
  const pathName = path.length > 1 ? path.join('/') : path[0] + '/'
  return handler(request, pathName)
}

export const GET = methodHandler
export const POST = methodHandler
export const PUT = methodHandler
export const DELETE = methodHandler
export const PATCH = methodHandler
