import { z } from 'zod'
import {
  ImageSchema,
  ItemSchema,
  TokenSchema,
  UserCreateSchema,
  UserSchema,
  UserUpdateSchema
} from './schemas'

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export type ApiProxyLoginResponse = { loggedIn: boolean }

export type ApiProxyLogoutResponse = { loggedOut: boolean }

// App: auth
export type Token = z.infer<typeof TokenSchema>

// App: items
export type Item = z.infer<typeof ItemSchema>
export type Items = Item[]
export type Image = z.infer<typeof ImageSchema>

// App: users
export type User = z.infer<typeof UserSchema>
export type Users = User[]
export type UserUpdate = z.infer<typeof UserUpdateSchema>
export type UserCreate = z.infer<typeof UserCreateSchema>
