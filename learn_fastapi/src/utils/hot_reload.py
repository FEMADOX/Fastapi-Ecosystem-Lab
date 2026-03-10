from fastapi import WebSocket, WebSocketDisconnect
from watchfiles import awatch

_clients: list[WebSocket] = []


async def _watch_files(match_path: str = ".") -> None:
    # async for _ in awatch(match_path, watch_filter=PythonFilter()):
    async for _ in awatch(match_path):
        disconnected = []
        for client in _clients:
            try:
                await client.send_text("reload")
            except WebSocketDisconnect:
                disconnected.append(client)
        for client in disconnected:
            _clients.remove(client)


async def _hot_reload_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    _clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _clients:
            _clients.remove(websocket)
