import { HttpMethod } from './types'

export interface RequestFactoryOptions {
  method?: HttpMethod
  pathParam?: string | null
  body?: unknown
  accessToken?: string | null
  headers?: HeadersInit
  queryParams?: Record<string, string>
}

export interface ApiProxyResponse<T> {
  data: T | undefined
  error?: string
}

export interface PromisePathProps {
  params: Promise<{ path: string[] }>
}
