import type { Item } from '../../common/types/api/resources'

export type CreateItemRequest = Omit<Item, 'id'>

export interface AuthProps {
  email: string
  password: string
}
