import type {
  Item,
  Items,
  Token,
  TokenV2,
  User,
  UserUpdate
} from '@/common/types/api/resources'
import 'server-only'
import {
  serverDelete,
  serverGet,
  serverPatch,
  serverPost
} from './server-fetch'
import type { AuthProps, CreateItemRequest, PatchItemRequest } from './types'

const API_PREFIX = '/latest'

// ==================  ITEMS  ==================
const ITEMS_BASE_PATH = `${API_PREFIX}/items/`

export const getItems = async () => await serverGet<Items>(`${ITEMS_BASE_PATH}`)

export const getItem = async (id: string) =>
  await serverGet<Item>(`${ITEMS_BASE_PATH}${id}`)

export const createItem = async (
  item: CreateItemRequest,
  accessToken: string
) => await serverPost<Item>(`${ITEMS_BASE_PATH}`, item, accessToken)

export const updateItem = async (
  id: string,
  item: PatchItemRequest,
  accessToken: string
) => await serverPatch<Item>(`${ITEMS_BASE_PATH}${id}`, item, accessToken)

export const uploadItemImage = async (
  id: string,
  imageFormData: FormData,
  accessToken: string
) =>
  await serverPost<Item>(
    `${ITEMS_BASE_PATH}image/${id}`,
    imageFormData,
    accessToken
  )

export const deleteItem = async (id: string, accessToken: string) =>
  await serverDelete(`${ITEMS_BASE_PATH}${id}`, accessToken)

// export const getItemImage = async (filename: string) =>
//   await serverGet(`${ITEMS_BASE_PATH}image/?filename=${encodeURIComponent(filename)}`)

export const getOwnerItems = async (userId?: string, accessToken?: string) => {
  return await serverGet<Items>(
    `${ITEMS_BASE_PATH}owner${userId ? `?order_id=${userId}` : ''}`,
    accessToken
  )
}

export const getOwnerItem = async (
  itemId: string,
  userId?: string,
  accessToken?: string
) => {
  return await serverGet<Item>(
    `${ITEMS_BASE_PATH}/order/${itemId}${userId ? `?order_id=${userId}` : ''}`,
    accessToken
  )
}

// ==================  AUTH  ==================
const AUTH_BASE_PATH = `${API_PREFIX}/auth/`

export const login = async (body: URLSearchParams) => {
  return await serverPost<TokenV2>(`${AUTH_BASE_PATH}token`, body, undefined, {
    'Content-Type': 'application/x-www-form-urlencoded'
  })
}

export const signup = async ({ email, password }: AuthProps) => {
  return await serverPost<User>(`${AUTH_BASE_PATH}register`, {
    email,
    password
  })
}

export const logout = async (accessToken: string) => {
  return await serverPost<null>(`${AUTH_BASE_PATH}logout`, {}, accessToken)
}

export const refreshAccessToken = async (headers: Headers) => {
  return await serverPost<Token>(
    `${AUTH_BASE_PATH}refresh`,
    {},
    undefined,
    headers
  )
}

// ==================  USER  ==================
const USER_BASE_PATH = `${API_PREFIX}/users/`

export const getMe = async (accessToken: string) => {
  return await serverGet<User>(`${USER_BASE_PATH}me`, accessToken)
}

export const updateCurrentUser = async (
  accessToken: string,
  userUpdate: UserUpdate,
  userId: string
) => {
  return await serverPatch<User>(
    `${USER_BASE_PATH}${userId}`,
    userUpdate,
    accessToken
  )
}

export const deleteCurrentUser = async (
  accessToken: string,
  userId: string
) => {
  return await serverDelete<null>(`${USER_BASE_PATH}${userId}`, accessToken)
}

// export const changePassword = async (passwordData: PasswordChangeRequest) => {
//   return await serverPost(`${USER_BASE_PATH}me/password`, passwordData)
// }

// export const requestPasswordReset = async (email: string) => {
//   return await serverPost(`${USER_BASE_PATH}request-password-reset`, { email })
// }

// export const resetPassword = async (resetData: PasswordResetRequest) => {
//   return await serverPost(`${USER_BASE_PATH}reset-password`, resetData)
// }
