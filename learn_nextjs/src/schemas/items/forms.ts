import { z } from 'zod'
import { Item } from '@/common/types/api/resources'
import {
  nonNegativeNumberFromForm,
  nullableImageUrlFromForm,
  stringFromForm
} from '@/app/utils/formInputValidators'

export const itemFormSchema: z.ZodType<Omit<Item, 'id' | 'user_id'>> = z
  .object({
    name: stringFromForm('Name is required'),
    description: stringFromForm('Description is required'),
    price: nonNegativeNumberFromForm('Price must be a non-negative number'),
    tax: nonNegativeNumberFromForm('Tax must be a non-negative number'),
    imageUrl: nullableImageUrlFromForm
  })
  .transform((data): Omit<Item, 'id' | 'user_id'> => ({
    name: data.name,
    description: data.description,
    price: data.price,
    tax: data.tax,
    image_url: data.imageUrl ?? undefined
  }))
