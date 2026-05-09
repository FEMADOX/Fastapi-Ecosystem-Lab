import type { CreateItemRequest, PatchItemRequest } from '@/app/api/types'
import type {
  itemCreateFormSchema,
  itemPatchFormSchema
} from '@/schemas/items/forms'

export type itemFormSchemas =
  | typeof itemCreateFormSchema
  | typeof itemPatchFormSchema

type ItemBaseSuccess<T extends itemFormSchemas> = {
  success: true
  userId: string
  accessToken: string
  itemData: T extends typeof itemCreateFormSchema
    ? CreateItemRequest
    : PatchItemRequest
}

type ItemBaseError = {
  success: false
  error: string
}

export type ItemBaseResult<T extends itemFormSchemas> =
  | ItemBaseSuccess<T>
  | ItemBaseError
