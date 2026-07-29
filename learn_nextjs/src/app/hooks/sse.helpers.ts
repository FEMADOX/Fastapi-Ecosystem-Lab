export const createSSEMessageHandler =
  <T>(onEvent: (event: T) => void) =>
  (message: { data: string }) => {
    onEvent(JSON.parse(message.data) as T)
  }
