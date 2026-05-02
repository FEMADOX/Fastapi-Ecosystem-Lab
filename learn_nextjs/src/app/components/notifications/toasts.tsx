'use client'

import { useEffect } from 'react'
import { toast } from 'sonner'
import type {
  SSEEventMap,
  SSEItemEvent,
  SSEToastProps
} from '@/app/api/sse/[channel]/types'
import { useAuth } from '@/app/hooks/useAuth'
import { useSSE } from '@/app/hooks/useSSE'

const NotificationListener = ({ channel, eventMap }: SSEToastProps) => {
  const { events } = useSSE<SSEItemEvent>(channel, true)

  useEffect(() => {
    events.forEach((event) => {
      eventMap[event.event]?.(event)
    })
  }, [events, eventMap])

  return null
}

const SSEBaseNotifications = (channel: string, eventMap: SSEEventMap) => {
  const {
    state: { status }
  } = useAuth()

  if (status !== 'authenticated') return null
  return <NotificationListener channel={channel} eventMap={eventMap} />
}

const globalEventMap: SSEEventMap = {
  'item.created': (event) =>
    toast.success(`New item created: ${event.payload.name}`)
}

const userEventMap: SSEEventMap = {
  'item.created': (event) =>
    toast.success(`You created a new item: ${event.payload.name}`),
  'item.updated': (event) =>
    toast.success(`Your item was updated: ${event.payload.name}`),
  'item.deleted': (event) =>
    toast.error(`Your item was deleted: ${event.payload.name}`),
  'item.image_updated': (event) =>
    toast.success(`Your item's image was updated: ${event.payload.name}`)
}

export const SSEGlobalNotifications = () =>
  SSEBaseNotifications('global', globalEventMap)

export const SSEUserNotifications = () =>
  SSEBaseNotifications('me', userEventMap)
