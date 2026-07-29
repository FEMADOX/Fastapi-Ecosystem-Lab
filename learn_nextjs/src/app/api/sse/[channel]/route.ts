import { type NextRequest, NextResponse } from 'next/server'
import { API_BASE_URL } from '@/common/const'
import type { PromiseChannelProps } from './types'

const handler = async (
  request: NextRequest,
  channel: string
): Promise<NextResponse> => {
  try {
    const token = request.cookies.get('access_token')?.value
    if (!token) return new NextResponse('Unauthorized', { status: 401 })

    const fastapiResponse = await fetch(
      `${API_BASE_URL}/latest/events/${channel}`,
      {
        method: 'GET',
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
          Accept: 'text/event-stream'
        },
        // signal: AbortSignal.timeout(0)
        signal: null
      }
    )

    if (!fastapiResponse.ok) {
      // Preserve FastAPI's status so EventSource follows its error path.
      return new NextResponse(fastapiResponse.body, {
        status: fastapiResponse.status,
        headers: {
          'Content-Type':
            fastapiResponse.headers.get('Content-Type') ?? 'application/json'
        }
      })
    }

    const readable = fastapiResponse.body
    if (!readable) throw new Error('No stream found in response')

    const response = new NextResponse(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive'
      }
    })

    return response
  } catch (error) {
    console.error('Error in SSE route:', error)
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    )
  }
}

const methodHandler = async (
  request: NextRequest,
  { params }: PromiseChannelProps
) => {
  const { channel } = await params
  return handler(request, channel)
}

export const GET = methodHandler
