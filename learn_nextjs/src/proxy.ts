import { jwtVerify } from 'jose'
import { type NextRequest, NextResponse } from 'next/server'

import { SECRET_KEY } from './common/const'

const PROTECTED = ['/items/new']
const AUTH_ONLY = ['/login', '/signup']
const JWT_SECRET = new TextEncoder().encode(SECRET_KEY)

export const proxy = async (request: NextRequest) => {
  const { pathname } = request.nextUrl
  const redirectTo = (redirectPath: string) =>
    NextResponse.redirect(new URL(`${redirectPath}`, request.url))

  const token = request.cookies.get('access_token')?.value

  const isProtected = PROTECTED.some((route) => pathname.startsWith(route))
  const isAuthOnly = AUTH_ONLY.some((route) => pathname.startsWith(route))

  if (isProtected) {
    if (!token) {
      // TODO (FENYXZ): Refresh the access token using refresh token before redirecting to login, if refresh token exists.
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set(
        'next',
        request.nextUrl.pathname + request.nextUrl.search
      )
      return NextResponse.redirect(loginUrl)
    }

    try {
      await jwtVerify(token, JWT_SECRET, {
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

  if (isAuthOnly && token) {
    return redirectTo('/')
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)']
}
