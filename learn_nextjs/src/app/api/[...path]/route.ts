import { cookies } from 'next/headers'
import { type NextRequest, NextResponse } from 'next/server'
import { API_BASE_URL as BACKEND_URL } from '@/common/const'
import { TokenSchema } from '@/common/schemas/api/resources'
import type { PromisePathProps } from '@/types/api/types'
import { refreshAccessToken } from '../server-endpoints'

const handler = async (
  request: NextRequest,
  pathname: string
): Promise<NextResponse> => {
  const [apiVersion, ...pathParts] = pathname.split('/')
  const apiPath = pathParts.join('/')

  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value

  const isRefresh = apiPath === 'auth/refresh'

  if (isRefresh) {
    const csrfToken = cookieStore.get('csrf_token')?.value
    const refreshToken = cookieStore.get('refresh_token')?.value

    if (!csrfToken || !refreshToken)
      return NextResponse.redirect(
        new URL('/login?reason=user_not_authenticated', request.url)
      )

    const headers = new Headers({
      'Content-Type': 'application/json',
      Cookie: `csrf_token=${csrfToken};refresh_token=${refreshToken}`,
      'X-CSRF-Token': csrfToken
    })

    const rawData = await refreshAccessToken(headers)
    if (!rawData.data && rawData.error) {
      return NextResponse.redirect(
        new URL('/login?reason=session_expired', request.url)
      )
    }

    const { data, error, success } = TokenSchema.safeParse(rawData)
    if (!success || error) {
      return NextResponse.redirect(
        new URL('/login?reason=refresh_failed', request.url)
      )
    }

    const response = NextResponse.json({ refreshed: true })

    const { access_token: accessToken, expires_in: accessExpiresIn } = data
    response.cookies.set('access_token', accessToken, {
      httpOnly: true,
      sameSite: 'lax',
      path: '/',
      expires: new Date(Date.now() + accessExpiresIn * 1000),
      secure: process.env.ENVIRONMENT === 'production'
    })

    return response
  }

  const refreshToken = cookieStore.get('refresh_token')?.value
  const forwardHeaders = new Headers()

  forwardHeaders.set(
    'Content-Type',
    request.headers.get('Content-Type') ?? 'application/json'
  )

  if (accessToken) {
    forwardHeaders.set('Authorization', `Bearer ${accessToken}`)
  }

  if (refreshToken && isRefresh) {
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
  const joinedPath = path.join('/')
  const hasTrailingSlash = request.nextUrl.pathname.endsWith('/')
  const shouldAppendSlash = hasTrailingSlash || path.length === 2
  const pathName = shouldAppendSlash ? `${joinedPath}/` : joinedPath
  return handler(request, pathName)
}

export const GET = methodHandler
export const POST = methodHandler
export const PUT = methodHandler
export const DELETE = methodHandler
export const PATCH = methodHandler
