(() => {
  const ws = new WebSocket("ws://localhost:8000/hot-reload")
  ws.onmessage = event => {
    if (event.data === "reload") location.reload()
  }
  ws.onclose = () => {
    setTimeout(() => location.reload(), 1000)
  }
})()
