import type { BuildHeadersOptions } from '@/types/api/types'

export const buildHeaders = (options: BuildHeadersOptions): Headers => {
  const { auth, hasBody, isSerializedBody } = options
  const headers = new Headers(options.headers)

  if (hasBody && !isSerializedBody && !headers.has('Content-Type'))
    headers.set('Content-Type', 'application/json')
  if (auth?.accessToken)
    headers.set('Authorization', `Bearer ${auth.accessToken}`)
  if (auth?.csrfToken) headers.set('X-CSRF-Token', auth.csrfToken)

  return headers
}

export const RETRYABLE_STATUS_CODES = new Set([500, 502, 503, 504])
export const RETRY_DELAYS_MS = [700, 1400, 2200]

export const wait = async (ms: number): Promise<void> => {
  await new Promise((resolve) => setTimeout(resolve, ms))
}

export const isRetryableFetchError = (error: unknown): boolean => {
  return (
    error instanceof TypeError ||
    (error instanceof Error && error.name === 'TimeoutError')
  )
}

export const parseErrorMessage = async (res: Response): Promise<string> => {
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
