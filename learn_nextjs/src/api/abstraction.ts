// FastAPI API endpoints in the frontend

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/latest'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

type RequestFactoryOptions = {
  method?: HttpMethod
  pathParam?: string | null
  body?: unknown
  token?: string | null
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
    token = null,
    headers = {},
    queryParams
  } = options

  const hasBody = body !== undefined

  const requestHeaders: HeadersInit = {
    ...(hasBody ? { 'Content-Type': 'application/json' } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
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
  get: <T>(endpoint: string, pathParam?: string | null, token?: string | null, queryParams?: Record<string, string>) => {
    return apiRequest<T>(endpoint, { method: 'GET', pathParam, token, queryParams })
  },
  post: <T, B = unknown>(endpoint: string, body: B, token?: string | null) => {
    return apiRequest<T>(endpoint, { method: 'POST', body, token })
  },
  put: <T, B = unknown>(endpoint: string, pathParam: string | null, body: B, token?: string | null) => {
    return apiRequest<T>(endpoint, { method: 'PUT', body, pathParam, token })
  },
  patch: <T, B = unknown>(endpoint: string, pathParam: string | null, body: B, token?: string | null) => {
    return apiRequest<T>(endpoint, { method: 'PATCH', body, pathParam, token })
  },
  delete: (endpoint: string, pathParam: string | null, token?: string | null) => {
    return apiRequest<void>(endpoint, { method: 'DELETE', pathParam, token })
  }
}
