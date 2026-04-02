// import { jwtVerify } from 'jose'
import { NextRequest, NextResponse } from 'next/server'
// import { SECRET_KEY } from './common/const'

const PROTECTED = ['/items/new']
const AUTH_ONLY = ['/login', '/signup']

export const proxy = async (request: NextRequest) => {
  const { pathname } = request.nextUrl
  const token = request.cookies.get('access_token')?.value

  const isProtected = PROTECTED.some((response) => pathname.startsWith(response))
  const isAuthOnly = AUTH_ONLY.some((response) => pathname.startsWith(response))

  if (isProtected) {
    if (!token) return NextResponse.redirect(new URL('/login', request.url))

    // TODO (FENYXZ): Re-enable JWT verification once we have a refresh token mechanism in place. For now, we just check if the token exists.
    // try {
    //   await jwtVerify(token, new TextEncoder().encode(SECRET_KEY), {
    //     algorithms: ['HS256']
    //   })
    //   return NextResponse.next()
    // } catch (error) {
    //   console.error('JWT verification failed in proxy', error)
    //   // Token expired or invalid - clear it and redirect
    //   const response = NextResponse.redirect(new URL('/login', request.url))
    //   response.cookies.delete('access_token')
    //   return response
    // }
  }

  if (isAuthOnly && token) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

export const config = { matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)'] }
