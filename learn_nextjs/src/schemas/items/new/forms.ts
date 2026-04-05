import z from 'zod'

import {
  nonNegativeNumberFromForm,
  nullableImageUrlFromForm,
  stringFromForm
} from '@/app/utils/formInputValidators'

export const clientItemSchema = z.object({
  userId: stringFromForm('User ID is required'),
  name: stringFromForm('Name is required'),
  description: stringFromForm('Description is required'),
  price: nonNegativeNumberFromForm('Price must be a non-negative number'),
  tax: nonNegativeNumberFromForm('Tax must be a non-negative number'),
  imageUrl: nullableImageUrlFromForm
})
