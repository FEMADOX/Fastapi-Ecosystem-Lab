import type { Item } from '@/common/types/api/resources'

interface BaseEvent {
  event: string
  payload: Record<string, unknown>
}

export interface ItemEvent extends BaseEvent {
  event: 'item.created' | 'item.updated' | 'item.deleted' | 'item.image_updated'
  payload: Item
}

export type SSEChannel = 'global' | 'me'
export type SSEBaseEvent = BaseEvent
export type SSEItemEvent = ItemEvent

export type PromiseChannelProps = {
  params: Promise<{ channel: SSEChannel }>
}
export type SSEEventMap = Record<string, (event: SSEItemEvent) => void>

export interface SSEToastProps {
  channel: string
  eventMap: SSEEventMap
}
