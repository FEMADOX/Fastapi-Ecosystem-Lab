export type Image = {
  name: string
  description: string
  contentType: string | null
  url: string
}

export type Item = {
  id: string
  userId: string
  name: string
  description: string
  price: number
  tax: number
  imageUrl: string | null
}

export type Items = Item[]

export type User = {
  id: string
  email: string
  isActive: boolean
  isSuperuser: boolean
}

export type Users = User[]

export type UserUpdate = {
  currentPassword: string
  email?: string
  newPassword?: string
}

export type Token = {
  accessToken: string
  tokenType: string
  expiresIn: number
  csrfToken: string
}
