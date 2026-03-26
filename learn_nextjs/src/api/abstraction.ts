// FastAPI API abstraction layer for Next.js frontend
// Provides a consistent interface for making API calls and handling responses/errors

import { API_BASE_URL } from '@/common/const'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

type RequestFactoryOptions = {
  method?: HttpMethod
  pathParam?: string | null
  body?: unknown
  accessToken?: string | null
  headers?: HeadersInit
  queryParams?: Record<string, string>
}

const buildUrl = (endpoint: string, pathParam?: string | null, queryParams?: Record<string, string>): string => {
  const base = `${API_BASE_URL}${endpoint}${pathParam ? `/${pathParam}` : ''}`
  if (queryParams && Object.keys(queryParams).length > 0) {
    return `${base}?${new URLSearchParams(queryParams).toString()}`
  }
  return base
}

const apiRequest = async <T>(endpoint: string, options: RequestFactoryOptions = {}): Promise<T> => {
  const {
    method = 'GET',
    pathParam = null,
    body,
    accessToken = null,
    headers = {},
    queryParams
  } = options

  const hasBody = body !== undefined

  const requestHeaders: HeadersInit = {
    ...(hasBody ? { 'Content-Type': 'application/json' } : {}),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...headers
  }

  const response = await fetch(buildUrl(endpoint, pathParam, queryParams), {
    method,
    headers: requestHeaders,
    ...(hasBody ? { body: JSON.stringify(body) } : {})
  })

  if (!response.ok) {
    const errorDetail = await response.text().catch(() => '')
    throw new Error(
      `Request failed (${method} ${endpoint}): ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export const api = {
  get: <T>(endpoint: string, pathParam?: string | null, accessToken?: string | null, queryParams?: Record<string, string>) => {
    return apiRequest<T>(endpoint, { method: 'GET', pathParam, accessToken, queryParams })
  },
  post: <T, B = unknown>(endpoint: string, body: B, accessToken?: string | null, contentType?: string) => {
    return apiRequest<T>(endpoint, { method: 'POST', body, accessToken, headers: contentType ? { 'Content-Type': contentType } : undefined })
  },
  put: <T, B = unknown>(endpoint: string, pathParam: string | null, body: B, accessToken?: string | null, contentType?: string) => {
    return apiRequest<T>(endpoint, { method: 'PUT', body, pathParam, accessToken, headers: contentType ? { 'Content-Type': contentType } : undefined })
  },
  patch: <T, B = unknown>(endpoint: string, pathParam: string | null, body: B, accessToken?: string | null, contentType?: string) => {
    return apiRequest<T>(endpoint, { method: 'PATCH', body, pathParam, accessToken, headers: contentType ? { 'Content-Type': contentType } : undefined })
  },
  delete: (endpoint: string, pathParam: string | null, accessToken?: string | null) => {
    return apiRequest<void>(endpoint, { method: 'DELETE', pathParam, accessToken })
  }
}
