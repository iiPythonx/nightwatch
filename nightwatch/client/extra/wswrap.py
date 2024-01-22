# Copyright (c) 2024 iiPython

# Modules
import orjson
from websockets import WebSocketCommonProtocol

# Main class
class ORJSONWebSocket():
    def __init__(self, ws: WebSocketCommonProtocol) -> None:
        self.ws = ws

    async def recv(self) -> dict:
        return orjson.loads(await self.ws.recv())

    async def send(self, data: dict) -> None:
        await self.ws.send(orjson.dumps(data))
