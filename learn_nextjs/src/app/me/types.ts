import type { Item, Items, User } from '@/common/types/api/resources'

export type MeActionState = {
  error?: string
  success?: string
} | null

export type MePageClientProps = {
  user: User
  ownedItems: Items
}

export interface ActionFeedbackProps {
  state: MeActionState
}

export interface OwnedItemEditorProps {
  item: Item
}
