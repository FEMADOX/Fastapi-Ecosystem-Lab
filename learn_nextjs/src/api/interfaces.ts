export interface Image {
  name: string
  description: string
  contentType: string | null
  url: string
}

export interface Item {
  id: string
  userId: string
  name: string
  description: string
  price: number
  tax: number
  imageUrl: string | null
}

export interface User {
  id: string
  email: string
  isActive: boolean
  isSuperuser: boolean
}

export type Users = User[]

export interface UserUpdate {
  currentPassword: string
  email?: string
  newPassword?: string
}

export interface Token {
  accessToken: string
  tokenType: string
  expiresIn: number
  csrfToken: string
}
