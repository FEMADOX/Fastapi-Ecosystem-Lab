import { z } from 'zod'

import { UserCreateSchema } from '@/common/schemas/api/resources'
import type { AuthFormVariant } from '@/types/auth/types'

const loginFormSchema = UserCreateSchema
const registerFormSchema = UserCreateSchema

export const authSchemas = {
  login: loginFormSchema,
  signup: registerFormSchema,
}

export type AuthParseResult =
  | { success: true }
  | { success: false; fieldErrors: Record<string, string> }

export function parseAuthForm(variant: AuthFormVariant, data: unknown): AuthParseResult {
  const schema = variant === 'login' ? loginFormSchema : registerFormSchema
  const result = schema.safeParse(data)
  if (result.success) {
    return { success: true }
  }
  const flattenedErrors = z.flattenError(result.error).fieldErrors
  const fieldErrors: Record<string, string> = {}
  for (const [field, messages] of Object.entries(flattenedErrors)) {
    if (Array.isArray(messages) && messages.length > 0) {
      fieldErrors[field] = messages[0] ?? 'Invalid value'
    }
  }
  return { success: false, fieldErrors }
}
