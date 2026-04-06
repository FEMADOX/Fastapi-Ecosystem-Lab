import type { z } from 'zod'

import type {
  ImageSchema,
  ItemSchema,
  TokenSchema,
  UserCreateSchema,
  UserSchema,
  UserUpdateSchema
} from '@/common/schemas/api/resources'

export type Token = z.infer<typeof TokenSchema>

export type Item = z.infer<typeof ItemSchema>
export type Items = Item[]
export type Image = z.infer<typeof ImageSchema>

export type User = z.infer<typeof UserSchema>
export type Users = User[]
export type UserUpdate = z.infer<typeof UserUpdateSchema>
export type UserCreate = z.infer<typeof UserCreateSchema>
