import { api, API_BASE_URL } from './abstraction'
import { Item, Items } from './types'

// ==================  ITEMS  ==================

export const getItems = async (): Promise<Items> => api.get<Items>('/items')

export const getItem = async (id: string): Promise<Item> => api.get<Item>('/items', id)

export const createItem = async (item: Omit<Item, 'id'>): Promise<Item> => api.post<Item>('/items', item)

export const updateItem = async (id: string, item: Omit<Item, 'id'>): Promise<Item> => api.put<Item>('/items', id, item)

export const patchItem = async (id: string, item: Omit<Item, 'id'>): Promise<Item> => api.patch<Item>('/items', id, item)

export const deleteItem = async (id: string): Promise<void> => api.delete('/items', id)

export const getItemImage = async (filename: string): Promise<string> => {
  const url = new URL(`${API_BASE_URL}/items/image/`)
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

  const response = await fetch(`${API_BASE_URL}/items/image/${id}`, {
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

  const response = await fetch(`${API_BASE_URL}/items/with-image/`, {
    method: 'POST',
    body: formData
  })
  if (!response.ok) {
    const errorDetail = await response.text().catch(() => '')
    throw new Error(`Failed to create item with image: ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`)
  }
  return response.json() as Promise<Item>
}

// ==================  USERS  ==================

// ==================  AUTH  ==================
