import { z } from 'zod'

export const ImageSchema = z.object({
  name: z.string({ message: 'Name is required' }),
  description: z.string().optional().default('No description provided'),
  content_type: z.string().nullable(),
  url: z.string()
})

export const ItemSchema = z.object({
  id: z.string(),
  user_id: z.string({ message: 'User ID is required' }),
  name: z.string({ message: 'Name is required' }),
  description: z.string().optional().default('No description provided'),
  price: z.number().nonnegative().gte(0).optional().default(0.0),
  tax: z.number().nonnegative().gte(0).optional().default(0.0),
  image_url: z.string().optional()
})

export const UserSchema = z.object({
  id: z.string(),
  email: z.email({ pattern: z.regexes.email, message: 'Invalid email address' }),
  is_active: z.boolean().default(true),
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

export const TokenV2Schema = z.object({
  access_token: z.string(),
  access_expires_in: z.number(),
  access_token_type: z.string().default('bearer'),
  refresh_token: z.string(),
  refresh_expires_in: z.number(),
  csrf_token: z.string()
})
