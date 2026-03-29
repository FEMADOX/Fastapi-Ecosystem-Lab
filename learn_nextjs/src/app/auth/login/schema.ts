import { UserCreate } from '@/app/api/interfaces'
import { z } from 'zod'
import { stringFromForm } from '@/app/utils/formInputValidators'

export const loginFormSchema: z.ZodType<UserCreate> = z.object({
  email: stringFromForm('Email is required'),
  password: stringFromForm('Password is required')
})
