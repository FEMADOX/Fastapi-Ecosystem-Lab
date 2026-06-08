import { z } from 'zod'

import {
  nonNegativeNumberFromForm,
  stringFromForm
} from '@/app/utils/formInputValidators'
import type { Item } from '@/common/types/api/resources'

export const itemCreateFormSchema: z.ZodType<Omit<Item, 'id' | 'user_id'>> = z
  .object({
    name: stringFromForm('Name is required'),
    description: stringFromForm('Description is required'),
    price: nonNegativeNumberFromForm('Price must be a non-negative number'),
    tax: nonNegativeNumberFromForm('Tax must be a non-negative number')
  })
  .transform(
    (data): Omit<Item, 'id' | 'user_id'> => ({
      name: data.name,
      description: data.description,
      price: data.price,
      tax: data.tax
    })
  )

export const itemPatchFormSchema: z.ZodType<
  Partial<Omit<Item, 'id' | 'user_id'>>
> = z
  .object({
    name: stringFromForm("Name can't be empty").optional(),
    description: stringFromForm("Description can't be empty").optional(),
    price: nonNegativeNumberFromForm(
      'Price must be a non-negative number'
    ).optional(),
    tax: nonNegativeNumberFromForm(
      'Tax must be a non-negative number'
    ).optional()
  })
  .transform(
    (data): Partial<Omit<Item, 'id' | 'user_id'>> => ({
      name: data.name,
      description: data.description,
      price: data.price,
      tax: data.tax
    })
  )
