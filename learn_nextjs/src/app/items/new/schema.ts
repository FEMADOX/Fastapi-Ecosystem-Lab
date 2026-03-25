import { Item } from '@/api/types'
import { z } from 'zod'

const stringFromForm = (message: string) =>
  z.preprocess(
    (value) => (typeof value === 'string' ? value.trim() : ''),
    z.string().min(1, message)
  )

const nonNegativeNumberFromForm = (message: string) =>
  z.preprocess((value) => {
    if (typeof value !== 'string') {
      return Number.NaN
    }

    const normalizedValue = value.trim()
    if (normalizedValue.length === 0) {
      return Number.NaN
    }

    const numericValue = Number(normalizedValue)
    return Number.isFinite(numericValue) ? numericValue : Number.NaN
  }, z.number().nonnegative(message))

const nullableImageUrlFromForm = z.preprocess((value) => {
  if (typeof value !== 'string') {
    return null
  }

  const normalizedValue = value.trim()
  return normalizedValue.length === 0 ? null : normalizedValue
}, z.string().url('Image URL must be a valid URL').nullable())

export const newItemFormSchema: z.ZodType<Omit<Item, 'id'>> = z.object({
  userId: stringFromForm('User ID is required'),
  name: stringFromForm('Name is required'),
  description: stringFromForm('Description is required'),
  price: nonNegativeNumberFromForm('Price must be a non-negative number'),
  tax: nonNegativeNumberFromForm('Tax must be a non-negative number'),
  imageUrl: nullableImageUrlFromForm
})
