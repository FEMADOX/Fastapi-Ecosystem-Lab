import { z } from 'zod'

export const ImageSchema = z.object({
  name: z.string(),
  description: z.string(),
  content_type: z.string().nullable(),
  url: z.string()
})

export const ItemSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  name: z.string(),
  description: z.string(),
  price: z.number().nonnegative().gte(0),
  tax: z.number().nonnegative().gte(0),
  image_url: z.string().optional()
})

export const UserSchema = z.object({
  id: z.string(),
  email: z.string(),
  is_active: z.boolean(),
  is_superuser: z.boolean().default(false)
})

export const UserUpdateSchema = z.object({
  current_password: z.string(),
  email: z.string().optional(),
  new_password: z.string().optional()
})

export const UserCreateSchema = z.object({
  email: z.email({ pattern: z.regexes.email }),
  password: z.string().min(8, 'Password must be at least 8 characters long')
})

export const TokenSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
  csrf_token: z.string()
})
