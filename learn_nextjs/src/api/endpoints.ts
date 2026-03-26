import { API_BASE_URL } from '@/common/const'
import { api } from './abstraction'
import { Item, Items, User, Token, UserUpdate } from './types'

// ==================  ITEMS  ==================
const ITEMS_PATH = '/items'

export const getItems = async (): Promise<Items> => api.get<Items>(ITEMS_PATH)

export const getItem = async (id: string): Promise<Item> => {
  return api.get<Item>(ITEMS_PATH, id)
}

export const createItem = async (item: Omit<Item, 'id'>): Promise<Item> => {
  return api.post<Item>(ITEMS_PATH, item)
}

export const updateItem = async (id: string, item: Omit<Item, 'id'>): Promise<Item> => {
  return api.put<Item>(ITEMS_PATH, id, item)
}

export const patchItem = async (id: string, item: Omit<Item, 'id'>): Promise<Item> => {
  return api.patch<Item>(ITEMS_PATH, id, item)
}

export const deleteItem = async (id: string): Promise<void> => {
  return api.delete(ITEMS_PATH, id)
}

export const getItemImage = async (filename: string): Promise<string> => {
  const url = new URL(`${API_BASE_URL}${ITEMS_PATH}/image/`)
  url.searchParams.set('filename', filename)

  const response = await fetch(url.toString())
  if (!response.ok) {
    throw new Error(`Failed to fetch image: ${response.status} ${response.statusText}`)
  }

  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

// POST /items/image/{id} — uploads image as multipart/form-data
export const uploadImageForItem = async (
  id: string,
  imageFile: File,
  caption = 'No description provided'
): Promise<Item> => {
  const formData = new FormData()
  formData.append('image_file', imageFile)
  formData.append('caption', caption)

  const response = await fetch(`${API_BASE_URL}${ITEMS_PATH}/image/${id}`, {
    method: 'POST',
    body: formData
  })
  if (!response.ok) {
    const errorDetail = await response.text().catch(() => '')
    throw new Error(`Failed to upload image: ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`)
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
): Promise<Item> => {
  const formData = new FormData()
  formData.append('name', name)
  formData.append('description', description)
  formData.append('price', String(price))
  formData.append('tax', String(tax))
  formData.append('caption', caption)
  if (imageFile) {
    formData.append('image_file', imageFile)
  }

  const response = await fetch(`${API_BASE_URL}${ITEMS_PATH}/with-image/`, {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  if (!response.ok) {
    const errorDetail = await response.text().catch(() => '')
    throw new Error(`Failed to create item with image: ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`)
  }
  return response.json() as Promise<Item>
}

// ==================  USERS  ==================
const USERS_PATH = '/users'

export const getMe = async (accessToken: string): Promise<User> => {
  return api.get<User>(`${USERS_PATH}/me`, null, accessToken)
}

export const getUser = async (id: string): Promise<User> => {
  return api.get<User>(USERS_PATH, id)
}

export const patchUser = async (id: string, user: UserUpdate): Promise<User> => {
  return api.patch<User>(USERS_PATH, id, user)
}

export const deleteUser = async (id: string, accessToken: string): Promise<void> => {
  return api.delete(USERS_PATH, id, accessToken)
}

// ==================  AUTH  ==================
const AUTH_PATH = '/auth'

export const register = async (
  email: string, password: string
): Promise<User> => {
  return api.post<User>(`${AUTH_PATH}/register`, { email, password })
}

export const login = async (
  email: string, password: string, contentType = 'application/x-www-form-urlencoded'
): Promise<Token> => {
  return api.post<Token>(`${AUTH_PATH}/token`, { email, password }, undefined, contentType)
}

export const refreshToken = async (accessToken: string): Promise<Token> => {
  return api.post<Token>(`${AUTH_PATH}/refresh`, {}, accessToken)
}

export const logout = async (accessToken: string): Promise<void> => {
  return api.post(`${AUTH_PATH}/logout`, {}, accessToken)
}
