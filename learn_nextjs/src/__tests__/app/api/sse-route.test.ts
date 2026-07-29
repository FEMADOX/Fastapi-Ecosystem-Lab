import { NextRequest } from 'next/server'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { GET } from '@/app/api/sse/[channel]/route'

const requestWithAccessToken = () =>
  new NextRequest('http://localhost/api/sse/me', {
    headers: { Cookie: 'access_token=expired-token' }
  })

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('SSE proxy route', () => {
  it('preserves an upstream authentication failure', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(
          Response.json({ detail: 'Invalid or expired token' }, { status: 401 })
        )
    )

    const response = await GET(requestWithAccessToken(), {
      params: Promise.resolve({ channel: 'me' })
    })

    expect(response.status).toBe(401)
    expect(response.headers.get('Content-Type')).toContain('application/json')
    await expect(response.json()).resolves.toEqual({
      detail: 'Invalid or expired token'
    })
  })

  it('continues streaming a successful upstream response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response('data: {"event":"item.created","payload":{}}\n\n', {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' }
        })
      )
    )

    const response = await GET(requestWithAccessToken(), {
      params: Promise.resolve({ channel: 'me' })
    })

    expect(response.status).toBe(200)
    expect(response.headers.get('Content-Type')).toContain('text/event-stream')
    await expect(response.text()).resolves.toContain('"item.created"')
  })
})
