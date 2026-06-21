import type { Item, UserUpdate } from '../../common/types/api/resources'

export type CreateItemRequest = Omit<Item, 'id'>

export type PatchItemRequest = Partial<CreateItemRequest>

export type DeleteAccountRequest = Pick<UserUpdate, 'current_password'>

export interface AuthProps {
  email: string
  password: string
}
