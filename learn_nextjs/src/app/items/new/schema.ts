import { Item } from '@/api/interfaces'
import { z } from 'zod'
import { nonNegativeNumberFromForm, nullableImageUrlFromForm, stringFromForm } from '@/app/utils/formInputValidators'

export const newItemFormSchema: z.ZodType<Omit<Item, 'id'>> = z.object({
  userId: stringFromForm('User ID is required'),
  name: stringFromForm('Name is required'),
  description: stringFromForm('Description is required'),
  price: nonNegativeNumberFromForm('Price must be a non-negative number'),
  tax: nonNegativeNumberFromForm('Tax must be a non-negative number'),
  imageUrl: nullableImageUrlFromForm
})
