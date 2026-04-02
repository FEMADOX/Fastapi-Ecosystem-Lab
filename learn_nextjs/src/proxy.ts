import { jwtVerify } from 'jose'
import { NextRequest, NextResponse } from 'next/server'
import { SECRET_KEY } from './common/const'

const PROTECTED = ['/items/new']
const AUTH_ONLY = ['/login', '/signup']
const JWT_SECRET = new TextEncoder().encode(SECRET_KEY)

export const proxy = async (request: NextRequest) => {
  const { pathname } = request.nextUrl
  const redirectTo = (redirectPath: string) => NextResponse.redirect(new URL(`${redirectPath}`, request.url))

  const token = request.cookies.get('access_token')?.value

  const isProtected = PROTECTED.some((route) => pathname.startsWith(route))
  const isAuthOnly = AUTH_ONLY.some((route) => pathname.startsWith(route))

  if (isProtected) {
    if (!token) return redirectTo('/login')

    // TODO (FENYXZ): Replace with full refresh token flow (Opción 2).
    // For now: verify signature only, ignore expiration.
    // The FastAPI API returns 401 on expired tokens → auth-provider handles logout.
    try {
      await jwtVerify(token, JWT_SECRET, {
        algorithms: ['HS256']
      })
    } catch (error) {
      // Only ignore expiration errors; block all other verification issues.
      const code = (error as { code?: string }).code
      if (code !== 'ERR_JWT_EXPIRED') {
        console.error('JWT verification failed in proxy, blocking request', error)
        const response = redirectTo('/login')
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

export const config = { matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)'] }
