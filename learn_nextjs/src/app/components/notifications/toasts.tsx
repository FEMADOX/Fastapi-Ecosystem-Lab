'use client'

import { useCallback } from 'react'
import type {
  SSEEvent,
  SSEEventMap,
  SSEToastProps
} from '@/app/api/sse/[channel]/types'
import { useAuth } from '@/app/hooks/useAuth'
import { useSSE } from '@/app/hooks/useSSE'
import { globalEventMap, userEventMap } from './events'
import { invokeHandler } from './toasts.helpers'

const NotificationListener = ({ channel, eventMap }: SSEToastProps) => {
  const handleEvent = useCallback(
    (event: SSEEvent) => invokeHandler(eventMap, event),
    [eventMap]
  )

  useSSE<SSEEvent>(channel, true, handleEvent)

  return null
}

const SSEBaseNotifications = (channel: string, eventMap: SSEEventMap) => {
  const {
    state: { status }
  } = useAuth()

  if (status !== 'authenticated') return null
  return <NotificationListener channel={channel} eventMap={eventMap} />
}

export const SSEGlobalNotifications = () =>
  SSEBaseNotifications('global', globalEventMap)

export const SSEUserNotifications = () =>
  SSEBaseNotifications('me', userEventMap)
