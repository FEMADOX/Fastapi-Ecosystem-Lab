// FastAPI API abstraction layer for Next.js frontend
// Provides a consistent interface for making API calls and handling responses/errors

import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import {
  APIBaseProps,
  ApiProxyResponse,
  RequestFactoryOptions
} from '@/types/api/types'

const getProxyBase = (): string => {
  // En el servidor (Server Components), fetch necesita URL absoluta
  // En el browser, la URL relativa /api/... funciona directamente
  if (typeof window === 'undefined') {
    const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'
    return `${appUrl}${NEXT_API_PROXY_PREFIX}`
  }
  return NEXT_API_PROXY_PREFIX
}

const buildUrl = (
  { endpoint, pathParam, apiVersion }: APIBaseProps,
  queryParams?: Record<string, string>
): string => {
  const base = `${getProxyBase()}${apiVersion}${endpoint}${pathParam ? `/${pathParam}` : ''}`
  if (queryParams && Object.keys(queryParams).length > 0) {
    return `${base}?${new URLSearchParams(queryParams).toString()}`
  }
  return base
}

const apiRequest = async <T>(
  endpoint: string,
  options: RequestFactoryOptions = {}
): Promise<ApiProxyResponse<T>> => {
  const {
    method = 'GET',
    pathParam = null,
    body,
    accessToken = null,
    headers = {},
    queryParams,
    apiVersion = '/latest'
  } = options

  const hasBody = body !== undefined
  const isSerializedBody =
    body instanceof URLSearchParams || body instanceof FormData

  const requestHeaders: HeadersInit = {
    ...(hasBody && !isSerializedBody
      ? { 'Content-Type': 'application/json' }
      : {}),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...headers
  }
  const response = await fetch(
    buildUrl({ endpoint, pathParam, apiVersion }, queryParams),
    {
      method,
      headers: requestHeaders,
      ...(hasBody
        ? { body: isSerializedBody ? (body as BodyInit) : JSON.stringify(body) }
        : {})
    }
  )

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`
    try {
      const errorData = (await response.json()) as unknown
      if (
        typeof errorData === 'object' &&
        errorData !== null &&
        'detail' in errorData &&
        typeof (errorData as Record<string, unknown>).detail === 'string'
      ) {
        message = String((errorData as Record<string, unknown>).detail)
      }
    } catch {}
    return { data: undefined, error: message }
  }

  if (response.status === 204) {
    return { data: undefined }
  }

  return { data: (await response.json()) as T }
}

export const api = {
  get: <T>(options: APIBaseProps, queryParams?: Record<string, string>) => {
    const { endpoint, pathParam, accessToken, apiVersion } = options
    return apiRequest<T>(endpoint, {
      method: 'GET',
      pathParam,
      accessToken,
      queryParams,
      apiVersion
    })
  },
  post: <T, B = unknown>(options: APIBaseProps, body?: B) => {
    const { endpoint, accessToken, apiVersion } = options
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body,
      accessToken,
      apiVersion
    })
  },
  put: <T, B = unknown>(options: APIBaseProps, body: B) => {
    const { endpoint, pathParam, accessToken, apiVersion } = options
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body,
      pathParam,
      accessToken,
      apiVersion
    })
  },
  patch: <T, B = unknown>(options: APIBaseProps, body: B) => {
    const { endpoint, pathParam, accessToken, apiVersion } = options
    return apiRequest<T>(endpoint, {
      method: 'PATCH',
      body,
      pathParam,
      accessToken,
      apiVersion
    })
  },
  delete: <T>(options: APIBaseProps) => {
    const { endpoint, pathParam, accessToken, apiVersion } = options
    return apiRequest<T>(endpoint, {
      method: 'DELETE',
      pathParam,
      accessToken,
      apiVersion
    })
  }
}
