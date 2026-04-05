import { BACKEND_API_VERSIONS } from '@/app/api/consts'

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export type ApiProxyLoginResponse = { loggedIn: boolean }

export type ApiProxyLogoutResponse = { loggedOut: boolean }

export type ApiVersion = (typeof BACKEND_API_VERSIONS)[number]

export type RequestFactoryOptions = {
  method?: HttpMethod
  pathParam?: string | null
  body?: unknown
  accessToken?: string | null
  headers?: HeadersInit
  queryParams?: Record<string, string>
  apiVersion?: ApiVersion
}

export type ApiProxyResponse<T> = {
  data: T | undefined
  error?: string
}

export type PromisePathProps = {
  params: Promise<{ path: string[] }>
}

export type APIBaseProps = {
  endpoint: string
  pathParam?: string | null
  accessToken?: string | null
  apiVersion?: ApiVersion
}
