import { z } from 'zod'
import { clientItemSchema } from '@/schemas/items/new/forms'
import type { SetFieldErrorsItemForm } from './types'

export const validateItemForm = (
  formElement: HTMLFormElement,
  setFieldErrors: SetFieldErrorsItemForm
) => {
  setFieldErrors({})
  const formData = new FormData(formElement)
  const rawFormData = Object.fromEntries(formData.entries())
  const parseResult = clientItemSchema.safeParse(rawFormData)

  if (!parseResult.success) {
    return {
      success: false,
      data: null,
      flattenedErrors: z.flattenError(parseResult.error).fieldErrors
    }
  }

  return { success: true, data: parseResult.data, flattenedErrors: {} }
}
