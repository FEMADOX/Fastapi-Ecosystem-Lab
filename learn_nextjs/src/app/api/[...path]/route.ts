import { type NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { API_BASE_URL } from '@/common/const'
import { PromisePathProps } from '../interfaces'
import { TokenSchema } from '../schemas'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || API_BASE_URL

const handler = async (
  request: NextRequest,
  pathname: string
): Promise<NextResponse> => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value

  const forwardHeaders = new Headers()
  forwardHeaders.set(
    'Content-Type',
    request.headers.get('Content-Type') ?? 'application/json'
  )
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
      headers: {
        'Content-Type':
          backendRes.headers.get('Content-Type') ?? 'application/json'
      }
    })
  }

  const isLogin = pathname === 'auth/token'
  const isLogout = pathname === 'auth/logout'

  if (isLogin) {
    const rawData: unknown = await backendRes.json()
    const { data, error } = await TokenSchema.safeParseAsync(rawData)
    if (!data || error) {
      return NextResponse.json(
        { detail: error.message ?? 'Invalid login response' },
        { status: 502 }
      )
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
  if (isLogout) {
    if (backendRes.status !== 204) {
      NextResponse.json(
        { detail: 'Invalid logout response' },
        { status: 502 }
      )
    }

    const response = NextResponse.json({ loggedOut: true })
    response.cookies.delete('access_token')
    // TODO (FENYXZ): Uncomment after implementing returning of refresh token from the API
    // response.cookies.delete('refresh_token', { path: '/' })
    return response
  }

  // Para cualquier otra ruta, pasar la respuesta tal cual
  const body = await backendRes.text()
  return new NextResponse(body, {
    status: backendRes.status,
    headers: {
      'Content-Type':
        backendRes.headers.get('Content-Type') ?? 'application/json'
    }
  })
}

const methodHanlder = async (
  request: NextRequest,
  { params }: PromisePathProps
) => {
  const { path } = await params
  return handler(request, path.join('/'))
}

export const GET = methodHanlder
export const POST = methodHanlder
export const PUT = methodHanlder
export const DELETE = methodHanlder
export const PATCH = methodHanlder
