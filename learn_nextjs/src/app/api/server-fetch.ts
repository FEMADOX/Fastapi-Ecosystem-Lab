import 'server-only'

import { API_BASE_URL } from '@/common/const'
import type { ApiProxyResponse } from '@/types/api/types'
import {
  buildHeaders,
  isRetryableFetchError,
  parseErrorMessage,
  RETRY_DELAYS_MS,
  RETRYABLE_STATUS_CODES,
  wait
} from './fetch.helpers'

export const serverRequestBase = async <T>(
  path: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  body?: unknown,
  accessToken?: string,
  headersProp?: HeadersInit
): Promise<ApiProxyResponse<T>> => {
  const isUrlEncodedBody = body instanceof URLSearchParams
  const isFormDataBody = body instanceof FormData

  const baseHeaders = headersProp
    ? headersProp
    : isUrlEncodedBody
      ? { 'Content-Type': 'application/x-www-form-urlencoded' }
      : undefined

  const headers = buildHeaders({
    auth: accessToken ? { accessToken } : undefined,
    hasBody: body !== undefined,
    isSerializedBody: isFormDataBody || isUrlEncodedBody,
    headers: baseHeaders
  })

  if (isUrlEncodedBody && !headers.has('Content-Type'))
    headers.set('Content-Type', 'application/x-www-form-urlencoded')

  for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}${path}`, {
        method,
        headers,
        body:
          body === undefined
            ? undefined
            : isFormDataBody
              ? body
              : isUrlEncodedBody
                ? body.toString()
                : JSON.stringify(body),
        signal: AbortSignal.timeout(1 * 60 * 1000) // 1 minute timeout for all server requests
      })

      if (!response.ok) {
        const parsedError = await parseErrorMessage(response)

        if (
          RETRYABLE_STATUS_CODES.has(response.status) &&
          attempt < RETRY_DELAYS_MS.length
        ) {
          await wait(RETRY_DELAYS_MS[attempt])
          continue
        }

        return { data: undefined, error: parsedError }
      }

      if (response.status === 204) return { data: undefined }

      return { data: (await response.json()) as T }
    } catch (error: unknown) {
      if (isRetryableFetchError(error) && attempt < RETRY_DELAYS_MS.length) {
        await wait(RETRY_DELAYS_MS[attempt])
        continue
      }

      return {
        data: undefined,
        error:
          'Backend is temporarily unavailable. Please retry in a few seconds.'
      }
    }
  }

  return {
    data: undefined,
    error: 'Backend did not respond in time. Please retry shortly.'
  }
}

export const serverGet = async <T>(
  path: string,
  accessToken?: string
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'GET', undefined, accessToken)
}

export const serverPost = async <T>(
  path: string,
  body: unknown,
  accessToken?: string,
  headers?: HeadersInit
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'POST', body, accessToken, headers)
}

export const serverPut = async <T>(
  path: string,
  body: unknown,
  accessToken?: string
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'PUT', body, accessToken)
}

export const serverDelete = async <T>(
  path: string,
  accessToken?: string,
  body?: unknown
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'DELETE', body, accessToken)
}

export const serverPatch = async <T>(
  path: string,
  body: unknown,
  accessToken?: string
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'PATCH', body, accessToken)
}
