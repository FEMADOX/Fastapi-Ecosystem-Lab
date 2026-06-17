import type { LucideIcon } from 'lucide-react'
import type { ComponentProps, ReactNode } from 'react'
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

export interface UpdateCardProps {
  title: string
  description: ReactNode
  content: ReactNode
  actionLabel: string
  dialogDescription: ReactNode
  icon: LucideIcon
  children: ReactNode
}

export interface ProfileUpdateFormProps {
  action: ComponentProps<'form'>['action']
  state: MeActionState
  isPending: boolean
  submitLabel: string
  pendingLabel: string
  submitVariant?: 'default' | 'destructive'
  formVariant?: 'email' | 'password'
  userEmail?: string
  children?: ReactNode
}

export type FieldsProps = Array<{
  label: string
  inputId: string
  inputName: string
  inputType: 'email' | 'password'
  defaultValue?: string
}>

export interface FieldsBaseComponentProps {
  fields: FieldsProps
}
