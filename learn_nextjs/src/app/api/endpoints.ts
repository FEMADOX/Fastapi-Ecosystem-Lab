import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import type {
  Item,
  Items,
  User,
  UserUpdate
} from '@/common/types/api/resources'
import type {
  ApiProxyLoginResponse,
  ApiProxyLogoutResponse,
  ApiProxyRefreshResponse,
  ApiVersion
} from '@/types/api/types'

import { api } from './abstraction'
import type { CreateItemRequest } from './types'

// ==================  ITEMS  ==================
const ITEMS_PATH = '/items'

export const getItems = async () => api.get<Items>({ endpoint: ITEMS_PATH })

export const getItem = async (id: string) => {
  return api.get<Item>({ endpoint: ITEMS_PATH, pathParam: id })
}

export const createItem = async (
  item: CreateItemRequest,
  accessToken: string
) => {
  return api.post<Item>({ endpoint: ITEMS_PATH }, item, {
    auth: { accessToken }
  })
}

export const updateItem = async (
  id: string,
  item: CreateItemRequest,
  accessToken: string
) => {
  return api.put<Item>({ endpoint: ITEMS_PATH, pathParam: id }, item, {
    auth: { accessToken }
  })
}

export const patchItem = async (
  id: string,
  item: CreateItemRequest,
  accessToken: string
) => {
  return api.patch<Item>({ endpoint: ITEMS_PATH, pathParam: id }, item, {
    auth: { accessToken }
  })
}

export const deleteItem = async (id: string, accessToken: string) => {
  return api.delete(
    { endpoint: ITEMS_PATH, pathParam: id },
    { auth: { accessToken } }
  )
}

export const getItemImage = async (filename: string) => {
  const query = new URLSearchParams({ filename }).toString()
  const response = await fetch(
    `${NEXT_API_PROXY_PREFIX}${ITEMS_PATH}/image/?${query}`
  )
  if (!response.ok) {
    throw new Error(
      `Failed to fetch image: ${response.status} ${response.statusText}`
    )
  }

  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

// POST /items/image/{id} — uploads image as multipart/form-data
export const uploadImageForItem = async (
  id: string,
  imageFile: File,
  caption = 'No description provided'
) => {
  const formData = new FormData()
  formData.append('image_file', imageFile)
  formData.append('caption', caption)

  const response = await fetch(
    `${NEXT_API_PROXY_PREFIX}${ITEMS_PATH}/image/${id}`,
    {
      method: 'POST',
      body: formData
    }
  )
  if (!response.ok) {
    const errorDetail = await response.text().catch(() => '')
    throw new Error(
      `Failed to upload image: ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`
    )
  }
  return response.json() as Promise<Item>
}

// POST /items/with-image/ — creates item + optional image as multipart/form-data
export const createItemWithImage = async (
  name: string,
  description = 'No description provided',
  price = 0,
  tax = 0,
  imageFile?: File,
  caption = 'No description provided'
) => {
  const formData = new FormData()
  formData.append('name', name)
  formData.append('description', description)
  formData.append('price', String(price))
  formData.append('tax', String(tax))
  formData.append('caption', caption)
  if (imageFile) {
    formData.append('image_file', imageFile)
  }

  const response = await fetch(
    `${NEXT_API_PROXY_PREFIX}${ITEMS_PATH}/with-image/`,
    {
      method: 'POST',
      body: formData
    }
  )
  if (!response.ok) {
    const errorDetail = await response.text().catch(() => '')
    throw new Error(
      `Failed to create item with image: ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`
    )
  }
  return response.json() as Promise<Item>
}

// ==================  USERS  ==================
const USERS_PATH = '/users'

export const getMe = async () => {
  return api.get<User>({ endpoint: `${USERS_PATH}/me` })
}

export const getUser = async (id: string) => {
  return api.get<User>({ endpoint: USERS_PATH, pathParam: id })
}

export const patchUser = async (id: string, user: UserUpdate) => {
  return api.patch<User>({ endpoint: USERS_PATH, pathParam: id }, user)
}

export const deleteUser = async (id: string) => {
  return api.delete({ endpoint: USERS_PATH, pathParam: id })
}

// ==================  AUTH  ==================
const AUTH_PATH = '/auth'
export const register = async (email: string, password: string) => {
  return api.post<User>(
    { endpoint: `${AUTH_PATH}/register` },
    { email, password }
  )
}

export const refreshAccessToken = async (csrfToken: string) => {
  return api.post<ApiProxyRefreshResponse>(
    { endpoint: `${AUTH_PATH}/refresh`, credentials: 'include' },
    {},
    { auth: { csrfToken } }
  )
}

export const logout = async () => {
  return api.post<ApiProxyLogoutResponse>(
    { endpoint: `${AUTH_PATH}/logout` },
    {}
  )
}

// ==================   (Versioned)   ==================

export const login = async (
  email: string,
  password: string,
  apiVersion: ApiVersion
) => {
  const body = new URLSearchParams({ username: email, password })
  return api.post<ApiProxyLoginResponse>(
    { endpoint: `${AUTH_PATH}/token`, apiVersion },
    body,
    {}
  )
}
