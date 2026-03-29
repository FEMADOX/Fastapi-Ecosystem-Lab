import { type NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { API_BASE_URL } from '@/common/const'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || API_BASE_URL

const handler = async (request: NextRequest, pathname: string): Promise<NextResponse> => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value

  // Construir headers para FastAPI, sin exponer las cookies del browser
  const forwardHeaders = new Headers()
  forwardHeaders.set('Content-Type', request.headers.get('Content-Type') ?? 'application/json')
  if (accessToken) {
    forwardHeaders.set('Authorization', `Bearer ${accessToken}`)
  }

  const backendRes = await fetch(`${BACKEND_URL}/${pathname}`, {
    method: request.method,
    headers: forwardHeaders,
    body: request.method !== 'GET' ? await request.text() : undefined
  })

  if (!backendRes.ok) {
    const body = await backendRes.text().catch(() => '')
    return new NextResponse(body, {
      status: backendRes.status,
      headers: { 'Content-Type': backendRes.headers.get('Content-Type') ?? 'application/json' }
    })
  }

  const isLogin = pathname === 'auth/token'
  // const isLogout = pathname === '/logout'

  // Si es login exitoso, guardar tokens en cookies HTTP-only
  if (isLogin && backendRes.ok) {
    const data: unknown = await backendRes.json()

    if (
      typeof data !== 'object' || data === null ||
      !('access_token' in data) || typeof data.access_token !== 'string' // ||
      // !('refresh_token' in data) || typeof data.refresh_token !== 'string'  UNCOMMENTAR después de implementar refresh tokens en el backend
    ) {
      return NextResponse.json({ error: 'Invalid login response' }, { status: 502 })
    }

    const response = NextResponse.json({ loggedIn: true })

    // Guardar tokens como HTTP-only cookies — JS nunca los ve
    response.cookies.set('access_token', data.access_token, {
      httpOnly: true,
      sameSite: 'lax',
      path: '/'
      // TODO (FENYXZ): en producción, agregar `secure: true` para que solo se envíen por HTTPS
      // secure: true, // descomenta en producción
    })
    // TODO (FENYXZ): Uncomment after implementing returning of refresh token from the API
    // response.cookies.set('refresh_token', data.refresh_token, {
    //   httpOnly: true,
    //   sameSite: 'lax',
    //   path: '/'
    //   TODO (FENYXZ): en producción, agregar `secure: true` para que solo se envíen por HTTPS
    //   secure: true, // descomenta en producción
    // })

    return response
  }
  // else if (isLogout) {
  //   // Si es logout, eliminar las cookies
  //   const data: unknown = await backendRes.json()
  //   if (typeof data !== 'object' || data === null || ) {
  //     return NextResponse.json({ error: 'Invalid logout response' }, { status: 502 })
  //   }

  //   const response = NextResponse.json({ loggedOut: true })
  //   response.cookies.delete('access_token', { path: '/' })
  //   response.cookies.delete('refresh_token', { path: '/' })
  //   return response
  // }

  // Para cualquier otra ruta, pasar la respuesta tal cual
  const body = await backendRes.text()
  return new NextResponse(body, {
    status: backendRes.status,
    headers: { 'Content-Type': backendRes.headers.get('Content-Type') ?? 'application/json' }
  })
}

export const GET = async (
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) => {
  const { path } = await params
  return handler(request, path.join('/'))
}

export const POST = async (
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) => {
  const { path } = await params
  return handler(request, path.join('/'))
}

// agrega PUT, DELETE, PATCH según necesites
