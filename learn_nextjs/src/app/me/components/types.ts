import type {
  ComponentProps,
  ForwardRefExoticComponent,
  HTMLAttributes,
  ReactNode,
  RefAttributes
} from 'react'
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

export interface AnimatedIconHandle {
  startAnimation: () => void
  stopAnimation: () => void
}

export type AnimatedIconComponent = ForwardRefExoticComponent<
  Omit<
    HTMLAttributes<HTMLDivElement>,
    | 'color'
    | 'onDrag'
    | 'onDragStart'
    | 'onDragEnd'
    | 'onAnimationStart'
    | 'onAnimationEnd'
    | 'onAnimationIteration'
  > & {
    size?: number
    duration?: number
    isAnimated?: boolean
    color?: string
  } & RefAttributes<AnimatedIconHandle>
>

export interface UpdateCardProps {
  title: string
  description: ReactNode
  content: ReactNode
  actionLabel: string
  dialogDescription: ReactNode
  icon: AnimatedIconComponent
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

export interface UpdateAccountComponentProps {
  userEmail: string
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
