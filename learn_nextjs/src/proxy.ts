import { jwtVerify } from 'jose'
import { type NextRequest, NextResponse } from 'next/server'
import { refreshAccessToken } from './app/api/server-endpoints'
import { SECRET_KEY } from './common/const'

const PROTECTED = ['/items/new', '/me']
const AUTH_ONLY = ['/login', '/signup']
const JWT_SECRET = new TextEncoder().encode(SECRET_KEY)

export const proxy = async (request: NextRequest) => {
  const { pathname } = request.nextUrl
  const redirectTo = (redirectPath: string) =>
    NextResponse.redirect(new URL(`${redirectPath}`, request.url))

  const accessToken = request.cookies.get('access_token')?.value

  const isProtected = PROTECTED.some((route) => pathname.startsWith(route))
  const isAuthOnly = AUTH_ONLY.some((route) => pathname.startsWith(route))

  if (isProtected) {
    if (!accessToken) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set(
        'next',
        request.nextUrl.pathname + request.nextUrl.search
      )

      const alreadyRefreshed =
        request.nextUrl.searchParams.get('refreshed') === '1'
      if (alreadyRefreshed) {
        return NextResponse.redirect(
          `${loginUrl}?reason=authentication-required`
        )
      }

      const refreshToken = request.cookies.get('refresh_token')?.value
      const csrfTokenCookies = request.cookies.get('csrf_token')?.value
      if (!refreshToken || !csrfTokenCookies)
        return NextResponse.redirect(
          `${loginUrl}?reason=user-not-authenticated`
        )

      const headers = new Headers({
        'Content-Type': 'application/json',
        Cookie: `csrf_token=${csrfTokenCookies};refresh_token=${refreshToken}`,
        'X-CSRF-Token': csrfTokenCookies
      })

      const refreshResponse = await refreshAccessToken(headers)
      if (refreshResponse.error || !refreshResponse.data) {
        console.error(
          `Failed to refresh token in proxy: ${refreshResponse.error}`
        )
        return NextResponse.redirect(
          `${loginUrl}?reason=fail-to-refresh-access-token`
        )
      }

      const {
        access_token: accessToken,
        csrf_token: csrfToken,
        expires_in: expiresIn
      } = refreshResponse.data

      const url = request.nextUrl.clone()
      url.searchParams.set('refreshed', '1')
      const response = NextResponse.redirect(url)

      response.cookies.set('access_token', accessToken, {
        httpOnly: true,
        path: '/',
        sameSite: 'lax',
        expires: new Date(Date.now() + expiresIn * 1000),
        secure: process.env.ENVIRONMENT === 'production'
      })
      response.cookies.set('csrf_token', csrfToken, {
        httpOnly: false,
        path: '/',
        sameSite: 'lax',
        secure: process.env.ENVIRONMENT === 'production'
      })
      return response
    }

    try {
      await jwtVerify(accessToken, JWT_SECRET, {
        algorithms: ['HS256']
      })
    } catch (error) {
      // Only ignore expiration errors; block all other verification issues.
      const code = (error as { code?: string }).code
      if (code !== 'ERR_JWT_EXPIRED') {
        console.error(
          'JWT verification failed in proxy, blocking request',
          error
        )
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set(
          'next',
          request.nextUrl.pathname + request.nextUrl.search
        )
        const response = NextResponse.redirect(loginUrl)
        response.cookies.delete('access_token')
        return response
      }
    }
  }

  if (isAuthOnly && accessToken) return redirectTo('/')

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)']
}
