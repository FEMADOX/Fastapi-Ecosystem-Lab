// FastAPI API abstraction layer for Next.js frontend
// Provides a consistent interface for making API calls and handling responses/errors

import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import { RequestFactoryOptions, ApiResponse } from './interfaces'

const buildUrl = (endpoint: string, pathParam?: string | null, queryParams?: Record<string, string>): string => {
  const base = `${NEXT_API_PROXY_PREFIX}${endpoint}${pathParam ? `/${pathParam}` : ''}`
  if (queryParams && Object.keys(queryParams).length > 0) {
    return `${base}?${new URLSearchParams(queryParams).toString()}`
  }
  return base
}

const apiRequest = async <T>(endpoint: string, options: RequestFactoryOptions = {}): Promise<ApiResponse<T>> => {
  const {
    method = 'GET',
    pathParam = null,
    body,
    accessToken = null,
    headers = {},
    queryParams
  } = options

  const hasBody = body !== undefined
  const isSerializedBody = body instanceof URLSearchParams || body instanceof FormData

  const requestHeaders: HeadersInit = {
    ...(hasBody && !isSerializedBody ? { 'Content-Type': 'application/json' } : {}),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...headers
  }
  const response = await fetch(buildUrl(endpoint, pathParam, queryParams), {
    method,
    headers: requestHeaders,
    ...(hasBody ? { body: isSerializedBody ? body as BodyInit : JSON.stringify(body) } : {})
  })

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`
    try {
      const errorData = await response.json() as unknown
      if (
        typeof errorData === 'object' && errorData !== null &&
        'detail' in errorData &&
        typeof (errorData as Record<string, unknown>).detail === 'string'
      ) {
        message = String((errorData as Record<string, unknown>).detail)
      }
    } catch { /* respuesta no era JSON, usar statusText */ }
    return { data: undefined, error: message }
  }

  if (response.status === 204) {
    return { data: undefined }
  }

  return { data: await response.json() as T }
}

export const api = {
  get: <T>(endpoint: string, pathParam?: string | null, accessToken?: string | null, queryParams?: Record<string, string>) => {
    return apiRequest<T>(endpoint, { method: 'GET', pathParam, accessToken, queryParams })
  },
  post: <T, B = unknown>(endpoint: string, body: B, accessToken?: string | null) => {
    return apiRequest<T>(endpoint, { method: 'POST', body, accessToken })
  },
  put: <T, B = unknown>(endpoint: string, pathParam: string | null, body: B, accessToken?: string | null) => {
    return apiRequest<T>(endpoint, { method: 'PUT', body, pathParam, accessToken })
  },
  patch: <T, B = unknown>(endpoint: string, pathParam: string | null, body: B, accessToken?: string | null) => {
    return apiRequest<T>(endpoint, { method: 'PATCH', body, pathParam, accessToken })
  },
  delete: (endpoint: string, pathParam: string | null, accessToken?: string | null) => {
    return apiRequest<void>(endpoint, { method: 'DELETE', pathParam, accessToken })
  }
}
