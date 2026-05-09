// FastAPI API abstraction layer for Next.js frontend
// Provides a consistent interface for making API calls and handling responses/errors

import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import type {
  APIBaseProps,
  ApiCallInit,
  ApiProxyResponse,
  BuildHeadersOptions,
  RequestFactoryOptions
} from '@/types/api/types'

const buildHeaders = (options: BuildHeadersOptions) => {
  const { auth, hasBody, isSerializedBody } = options
  const headers = new Headers(options.headers)

  if (hasBody && !isSerializedBody && !headers.has('Content-Type'))
    headers.set('Content-Type', 'application/json')
  if (auth?.accessToken)
    headers.set('Authorization', `Bearer ${auth.accessToken}`)
  if (auth?.csrfToken) headers.set('X-CSRF-Token', auth.csrfToken)

  return headers
}

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
    headers = {},
    queryParams,
    apiVersion = '/latest',
    credentials = 'include',
    auth
  } = options

  const hasBody = body !== undefined
  const isSerializedBody =
    body instanceof URLSearchParams || body instanceof FormData

  const requestHeaders = buildHeaders({
    auth,
    hasBody,
    isSerializedBody,
    headers
  })
  const baseUrl = buildUrl({ endpoint, pathParam, apiVersion }, queryParams)
  const response = await fetch(baseUrl, {
    method,
    headers: requestHeaders,
    ...(hasBody
      ? { body: isSerializedBody ? (body as BodyInit) : JSON.stringify(body) }
      : {}),
    credentials
  })

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
  get: <T>(options: APIBaseProps, init?: ApiCallInit) => {
    const { endpoint, pathParam, apiVersion } = options
    const { auth, credentials, headers, queryParams } = init ?? {}
    return apiRequest<T>(endpoint, {
      method: 'GET',
      pathParam,
      headers,
      auth,
      credentials,
      queryParams,
      apiVersion
    })
  },
  post: <T, B = unknown>(
    options: APIBaseProps & {
      credentials?: RequestCredentials
    },
    body?: B,
    init?: ApiCallInit
  ) => {
    const { endpoint, apiVersion } = options
    const { auth, credentials, headers, queryParams } = init ?? {}
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body,
      apiVersion,
      headers,
      credentials,
      auth,
      queryParams
    })
  },
  put: <T, B = unknown>(options: APIBaseProps, body?: B, init?: ApiCallInit) => {
    const { endpoint, apiVersion } = options
    const { auth, credentials, headers, queryParams } = init ?? {}
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body,
      apiVersion,
      headers,
      credentials,
      auth,
      queryParams
    })
  },
  patch: <T, B = unknown>(
    options: APIBaseProps,
    body?: B,
    init?: ApiCallInit
  ) => {
    const { endpoint, apiVersion } = options
    const { auth, credentials, headers, queryParams } = init ?? {}
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body,
      apiVersion,
      headers,
      credentials,
      auth,
      queryParams
    })
  },
  delete: <T>(options: APIBaseProps, init?: ApiCallInit) => {
    const { endpoint, apiVersion } = options
    const { auth, credentials, headers, queryParams } = init ?? {}
    return apiRequest<T>(endpoint, {
      method: 'DELETE',
      apiVersion,
      headers,
      credentials,
      auth,
      queryParams
    })
  }
}
