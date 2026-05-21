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
  const { events } = useSSE<SSEEvent>(channel, true)

  useEffect(() => {
    events.forEach((event) => {
      const handler = eventMap[event.event]
      if (handler) {
        const message = handler.toastMessage(event)
        switch (handler.toastType) {
          case 'success':
            toast.success(message)
            break
          case 'error':
            toast.error(message)
            break
          case 'info':
            toast.info(message)
            break
          case 'warning':
            toast.warning(message)
            break
        }
      }
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
  'item.created': {
    toastType: 'success',
    toastMessage: (event) => `New item created: ${event.payload.name}`
  }
}

const userEventMap: SSEEventMap = {
  'item.created': {
    toastType: 'success',
    toastMessage: (event) => `You created a new item: ${event.payload.name}`
  },
  'item.updated': {
    toastType: 'info',
    toastMessage: (event) => `Your item was updated: ${event.payload.name}`
  },
  'item.deleted': {
    toastType: 'error',
    toastMessage: (event) => `Your item was deleted: ${event.payload.name}`
  },
  'item.image_updated': {
    toastType: 'info',
    toastMessage: (event) => `Your item's image was updated: ${event.payload.name}`
  },
  'auth.registered': {
    toastType: 'success',
    toastMessage: (event) => `Welcome! Account created successfully.`
  },
  'auth.logged_in': {
    toastType: 'success',
    toastMessage: (event) => `Welcome back! You are now logged in.`
  },
  'auth.logged_out': {
    toastType: 'info',
    toastMessage: (event) => `You have been logged out.`
  },
  'user.account_updated': {
    toastType: 'info',
    toastMessage: (event) => {
      const fields = event.payload.changed_fields as string[] | undefined
      const fieldMessages = fields?.join(', ') || ''
      return `Your account was updated. Changed: ${fieldMessages}`
    }
  },
  'user.account_deleted': {
    toastType: 'warning',
    toastMessage: (event) => `Your account has been deleted.`
  }
}

export const SSEGlobalNotifications = () =>
  SSEBaseNotifications('global', globalEventMap)

export const SSEUserNotifications = () =>
  SSEBaseNotifications('me', userEventMap)
