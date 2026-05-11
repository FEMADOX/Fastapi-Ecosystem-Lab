import { z } from 'zod'

export const profileEmailSchema = z.object({
  email: z.email({
    pattern: z.regexes.email,
    message: 'Invalid email address'
  }),
  currentPassword: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters long' })
})

export const profilePasswordSchema = z
  .object({
    currentPassword: z
      .string()
      .min(8, { message: 'Password must be at least 8 characters long' }),
    newPassword: z
      .string()
      .min(8, { message: 'Password must be at least 8 characters long' }),
    confirmPassword: z
      .string()
      .min(1, { message: 'Please confirm your password' })
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'New password and confirmation must match',
    path: ['confirmPassword']
  })
