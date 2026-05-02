import { EventSourcePolyfill } from 'event-source-polyfill'
import { useEffect, useState } from 'react'
import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import type { SSEBaseEvent } from '../api/sse/[channel]/types'

export const useSSE = <T extends SSEBaseEvent>(
  channel: string,
  enabled: boolean
) => {
  const [events, setEvents] = useState<T[]>([])
  const [, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState<boolean>(false)

  useEffect(() => {
    if (!enabled) return

    const eventSource = new EventSourcePolyfill(
      `${NEXT_API_PROXY_PREFIX}/sse/${channel}`,
      {
        withCredentials: true
      }
    )

    eventSource.onmessage = (event) => {
      const data: T = JSON.parse(event.data)
      setEvents((prevEvents) => [...prevEvents, data])
      setLoading(true)
    }

    eventSource.onerror = () => {
      setError('Connection lost. Reconnecting...')
      setLoading(false)
    }

    return () => {
      eventSource.close()
      setIsConnected(false)
    }
  }, [channel, enabled])

  return { events, error, isConnected }
}
