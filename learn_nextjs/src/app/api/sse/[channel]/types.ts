import type { Item } from '@/common/types/api/resources'

interface BaseEvent {
  event: string
  payload: Record<string, unknown>
}

export interface ItemEvent extends BaseEvent {
  event: 'item.created' | 'item.updated' | 'item.deleted' | 'item.image_updated'
  payload: Item
}

export interface AuthEvent extends BaseEvent {
  event: 'auth.registered' | 'auth.logged_in' | 'auth.logged_out'
  payload: {
    user_id: string
    email?: string
    [key: string]: unknown
  }
}

export interface UserEvent extends BaseEvent {
  event: 'user.account_updated' | 'user.account_deleted'
  payload: {
    user_id: string
    changed_fields?: string[]
    [key: string]: unknown
  }
}

export type SSEChannel = 'global' | 'me'
export type SSEBaseEvent = BaseEvent
export type SSEEvent = ItemEvent | AuthEvent | UserEvent

/**
 * Map of SSE event names to toast display functions.
 */
// export type SSEEventMap = {
//   [eventName: string]: {
//     toastType: 'success' | 'error' | 'info' | 'warning'
//     toastMessage: (event: SSEEvent) => string
//   }
// }

// export interface SSEToastProps {
//   channel: string
//   eventMap: SSEEventMap
// }

export type SSEItemEvent = ItemEvent

export type PromiseChannelProps = {
  params: Promise<{ channel: SSEChannel }>
}

export type SSEEventByPrefix = {
  [K in SSEEvent as K['event']]: K['event'] extends `item.${string}`
    ? ItemEvent
    : K['event'] extends `auth.${string}`
      ? AuthEvent
      : K['event'] extends `user.${string}`
        ? UserEvent
        : never
}

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export type SSEEventMap = {
  [K in keyof SSEEventByPrefix]?: {
    toastType: ToastType
    toastMessage: (event: SSEEventByPrefix[K]) => string
  }
}

export interface SSEToastProps {
  channel: string
  eventMap: SSEEventMap
}
