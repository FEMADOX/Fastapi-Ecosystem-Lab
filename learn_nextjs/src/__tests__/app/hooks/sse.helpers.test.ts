import { describe, expect, it, vi } from 'vitest'
import { createSSEMessageHandler } from '@/app/hooks/sse.helpers'

describe('createSSEMessageHandler', () => {
  it('delivers each incoming message exactly once', () => {
    const onEvent = vi.fn()
    const handleMessage = createSSEMessageHandler(onEvent)

    handleMessage(
      new MessageEvent('message', {
        data: JSON.stringify({ event: 'item.created', payload: { id: 'one' } })
      })
    )
    handleMessage(
      new MessageEvent('message', {
        data: JSON.stringify({ event: 'item.updated', payload: { id: 'two' } })
      })
    )

    expect(onEvent).toHaveBeenCalledTimes(2)
    expect(onEvent).toHaveBeenNthCalledWith(1, {
      event: 'item.created',
      payload: { id: 'one' }
    })
    expect(onEvent).toHaveBeenNthCalledWith(2, {
      event: 'item.updated',
      payload: { id: 'two' }
    })
  })
})
