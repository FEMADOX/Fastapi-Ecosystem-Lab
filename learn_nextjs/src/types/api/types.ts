import type { BACKEND_API_VERSIONS } from '@/app/api/consts'

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export type ApiProxyLoginResponse = { loggedIn: boolean }
export type ApiProxyLogoutResponse = { loggedOut: boolean }
export type ApiProxyRefreshResponse = { refreshed: boolean }

export type ApiVersion = (typeof BACKEND_API_VERSIONS)[number]

type AuthContext = {
  accessToken?: string
  csrfToken?: string
}

export interface BuildHeadersOptions {
  auth?: AuthContext
  headers?: HeadersInit
  hasBody?: boolean
  isSerializedBody?: boolean
}

export type RequestFactoryOptions = {
  method?: HttpMethod
  pathParam?: string | null
  body?: unknown
  headers?: HeadersInit
  auth?: AuthContext
  queryParams?: Record<string, string>
  apiVersion?: ApiVersion
  credentials?: RequestCredentials
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
  apiVersion?: ApiVersion
}

export type ApiCallInit = {
  auth?: AuthContext
  headers?: HeadersInit
  queryParams?: Record<string, string>
  credentials?: RequestCredentials
}
