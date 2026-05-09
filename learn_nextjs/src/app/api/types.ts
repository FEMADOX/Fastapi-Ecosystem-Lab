import type { Item } from '../../common/types/api/resources'

export type CreateItemRequest = Omit<Item, 'id'>

export type PatchItemRequest = Partial<CreateItemRequest>

export interface AuthProps {
  email: string
  password: string
}
