import { toast } from 'sonner'
import type {
  SSEEvent,
  SSEEventMap,
  ToastType
} from '@/app/api/sse/[channel]/types'

export const showToast = (type: ToastType, message: string) => {
  switch (type) {
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

export const invokeHandler = (eventMap: SSEEventMap, event: SSEEvent) => {
  const handler = eventMap[event.event]
  if (!handler) return

  const message = handler.toastMessage(event as never)
  showToast(handler.toastType, message)
}
