import type { Item, Items, User } from '@/common/types/api/resources'

export interface OwnedItemEditorProps {
  item: Item
}

export interface TabProfileProps {
  user: User
  isActive: boolean
}

export interface TabItemProps {
  ownedItems: Items
  isActive: boolean
}
