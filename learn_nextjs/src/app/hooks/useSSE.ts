import { EventSourcePolyfill } from 'event-source-polyfill'
import { useEffect, useRef, useState } from 'react'
import { NEXT_API_PROXY_PREFIX } from '@/common/const'
import type { SSEBaseEvent } from '../api/sse/[channel]/types'

export const useSSE = <T extends SSEBaseEvent>(
  channel: string,
  enabled: boolean
) => {
  const eventSourceRef = useRef<EventSourcePolyfill | null>(null)

  const [events, setEvents] = useState<T[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState<boolean>(false)

  useEffect(() => {
    if (!enabled) {
      eventSourceRef.current?.close()
      eventSourceRef.current = null
      setIsConnected(false)
      setIsLoading(false)
      return
    }

    if (eventSourceRef.current) return

    setIsLoading(true)
    setError(null)

    const eventSource = new EventSourcePolyfill(
      `${NEXT_API_PROXY_PREFIX}/sse/${channel}`,
      {
        withCredentials: true,
        heartbeatTimeout: 60 * 60 * 1000
      }
    )

    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      setIsConnected(true)
      setIsLoading(false)
      setError(null)
    }

    eventSource.onmessage = (event) => {
      const data: T = JSON.parse(event.data)
      setEvents((prevEvents) => [...prevEvents, data])
    }

    eventSource.onerror = () => {
      setIsConnected(false)
      setIsLoading(false)
      setError('Connection lost. Reconnecting...')
    }

    return () => {
      eventSource.close()
      eventSourceRef.current = null
      setIsConnected(false)
      setIsLoading(false)
    }
  }, [channel, enabled])

  return { events, error, isConnected, isLoading }
}
