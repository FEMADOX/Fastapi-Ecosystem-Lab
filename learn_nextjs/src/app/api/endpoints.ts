import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import {
  Item,
  Items,
  Token,
  User,
  UserUpdate
} from '@/common/types/api/resources'
import {
  ApiProxyLoginResponse,
  ApiProxyLogoutResponse,
  ApiVersion
} from '@/types/api/types'

import { api } from './abstraction'

// ==================  ITEMS  ==================
const ITEMS_PATH = '/items'

export const getItems = async () => api.get<Items>({ endpoint: ITEMS_PATH })

export const getItem = async (id: string) => {
  return api.get<Item>({ endpoint: ITEMS_PATH, pathParam: id })
}

export const createItem = async (item: Omit<Item, 'id'>) => {
  return api.post<Item>({ endpoint: ITEMS_PATH }, item)
}

export const updateItem = async (id: string, item: Omit<Item, 'id'>) => {
  return api.put<Item>({ endpoint: ITEMS_PATH, pathParam: id }, item)
}

export const patchItem = async (id: string, item: Omit<Item, 'id'>) => {
  return api.patch<Item>({ endpoint: ITEMS_PATH, pathParam: id }, item)
}

export const deleteItem = async (id: string) => {
  return api.delete({ endpoint: ITEMS_PATH, pathParam: id })
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

// ==================   (Versioned)   ==================
export const register = async (
  email: string,
  password: string,
  apiVersion?: ApiVersion
) => {
  return api.post<User>(
    { endpoint: `${AUTH_PATH}/register`, apiVersion },
    { email, password }
  )
}

export const login = async (
  email: string,
  password: string,
  apiVersion?: ApiVersion
) => {
  const body = new URLSearchParams({ username: email, password })
  return api.post<ApiProxyLoginResponse>(
    { endpoint: `${AUTH_PATH}/token`, apiVersion },
    body
  )
}

export const refreshToken = async (apiVersion?: ApiVersion) => {
  return api.post<Token>({ endpoint: `${AUTH_PATH}/refresh`, apiVersion }, {})
}

export const logout = async (apiVersion?: ApiVersion) => {
  return api.post<ApiProxyLogoutResponse>(
    { endpoint: `${AUTH_PATH}/logout`, apiVersion },
    {}
  )
}
