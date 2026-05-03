import type {
  Item,
  Items,
  Token,
  TokenV2,
  User
} from '@/common/types/api/resources'
import 'server-only'
import { serverGet, serverPost } from './server-fetch'
import type { AuthProps, CreateItemRequest } from './types'

// ==================  ITEMS  ==================
export const getItems = async () => await serverGet<Items>('/latest/items')
export const getItem = async (id: string) =>
  await serverGet<Item>(`/latest/items/${id}`)
export const createItem = async (
  item: CreateItemRequest,
  accessToken: string
) => await serverPost<Item>('/latest/items/', item, accessToken)

// export const updateItem = async (id: string, item: CreateItemRequest) =>
//   await serverPut(`/latest/items/${id}`, item)

// export const deleteItem = async (id: string) => await serverDelete(`/latest/items/${id}`)

// export const getItemImage = async (filename: string) =>
//   await serverGet(`/latest/items/image/?filename=${encodeURIComponent(filename)}`)

// export const uploadImageForItem = async (id: string, imageFile: File) => {
//   const formData = new FormData()
//   formData.append('image', imageFile)
//   return await serverPost(`/latest/items/image/${id}`, formData)
// }

// ==================  AUTH  ==================
export const login = async ({ email, password }: AuthProps) => {
  return await serverPost<TokenV2>('/latest/auth/login', { email, password })
}
export const signup = async ({ email, password }: AuthProps) => {
  return await serverPost<User>('/latest/auth/signup', { email, password })
}
export const logout = async (accessToken: string) => {
  return await serverPost<null>('/latest/auth/logout', {}, accessToken)
}
export const refreshToken = async () => {
  return await serverPost<Token>('/latest/auth/refresh', {})
}

// ==================  USER  ==================
export const getMe = async (accessToken: string) => {
  return await serverGet<User>('/latest/users/me', accessToken)
}

// export const updateCurrentUser = async (userUpdate: UserUpdate) => {
//   return await serverPut('/latest/users/me', userUpdate)
// }

// export const changePassword = async (passwordData: PasswordChangeRequest) => {
//   return await serverPost('/latest/users/me/password', passwordData)
// }

// export const requestPasswordReset = async (email: string) => {
//   return await serverPost('/latest/auth/request-password-reset', { email })
// }

// export const resetPassword = async (resetData: PasswordResetRequest) => {
//   return await serverPost('/latest/auth/reset-password', resetData)
// }
