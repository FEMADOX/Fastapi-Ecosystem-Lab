import type { ApiVersion, HttpMethod } from '@/types/api/types'

export interface RequestFactoryOptions {
  method?: HttpMethod
  pathParam?: string | null
  body?: unknown
  accessToken?: string | null
  headers?: HeadersInit
  queryParams?: Record<string, string>
  apiVersion?: ApiVersion
}

export interface ApiProxyResponse<T> {
  data: T | undefined
  error?: string
}

export interface PromisePathProps {
  params: Promise<{ path: string[] }>
}

export interface APIBaseProps {
  endpoint: string
  pathParam?: string | null
  accessToken?: string | null
  apiVersion?: ApiVersion
}
