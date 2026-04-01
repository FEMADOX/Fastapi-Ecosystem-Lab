import { z } from 'zod'

export const ImageSchema = z.object({
  name: z.string(),
  description: z.string().optional(),
  content_type: z.string().nullable(),
  url: z.string()
})

export const ItemSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  price: z.number().nonnegative().gte(0).optional(),
  tax: z.number().nonnegative().gte(0).optional(),
  image_url: z.string().optional()
})

export const UserSchema = z.object({
  id: z.string(),
  email: z.email({ pattern: z.regexes.email, message: 'Invalid email address' }),
  is_active: z.boolean(),
  is_superuser: z.boolean().default(false)
})

export const UserUpdateSchema = z.object({
  current_password: z.string().min(8, { message: 'Password must be at least 8 characters long' }),
  email: z.email({ pattern: z.regexes.email, message: 'Invalid email address' }).optional(),
  new_password: z.string().min(8, { message: 'Password must be at least 8 characters long' }).optional()
})

export const UserCreateSchema = z.object({
  email: z.email({ pattern: z.regexes.email, message: 'Invalid email address' }),
  password: z.string().min(8, { message: 'Password must be at least 8 characters long' })
})

export const TokenSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
  csrf_token: z.string()
})
