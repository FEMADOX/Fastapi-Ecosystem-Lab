import 'server-only'

import { cookies } from 'next/headers'

import { API_BASE_URL } from '@/common/const'
import type { ApiProxyResponse } from '@/types/api/types'

const RETRYABLE_STATUS_CODES = new Set([500, 502, 503, 504])
const RETRY_DELAYS_MS = [700, 1400, 2200]

const wait = async (ms: number): Promise<void> => {
  await new Promise((resolve) => setTimeout(resolve, ms))
}

const isRetryableFetchError = (error: unknown): boolean => {
  return (
    error instanceof TypeError ||
    (error instanceof Error && error.name === 'TimeoutError')
  )
}

export const getAuthHeaders = async (): Promise<HeadersInit> => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {}
}

const parseErrorMessage = async (res: Response): Promise<string> => {
  let message = `${res.status} ${res.statusText}`
  try {
    const data = (await res.json()) as unknown
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as Record<string, unknown>).detail === 'string'
    ) {
      message = String((data as Record<string, unknown>).detail)
    }
  } catch {}
  return message
}

export const serverRequestBase = async <T>(
  path: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  body?: unknown,
  accessToken?: string,
  headersProp?: HeadersInit
): Promise<ApiProxyResponse<T>> => {
  const isUrlEncodedBody = body instanceof URLSearchParams
  const isFormDataBody = body instanceof FormData

  const headers: HeadersInit = headersProp ?? {
    ...(isFormDataBody
      ? {}
      : {
          'Content-Type': isUrlEncodedBody
            ? 'application/x-www-form-urlencoded'
            : 'application/json'
        }),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
  }

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
  accessToken?: string
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'DELETE', undefined, accessToken)
}

export const serverPatch = async <T>(
  path: string,
  body: unknown,
  accessToken?: string
): Promise<ApiProxyResponse<T>> => {
  return serverRequestBase<T>(path, 'PATCH', body, accessToken)
}
