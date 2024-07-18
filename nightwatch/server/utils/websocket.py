# Copyright (c) 2024 iiPython

# Modules
import orjson
from websockets import WebSocketCommonProtocol

class NightwatchClient():
    """This class acts as a wrapper on top of WebSocketCommonProtocol that implements
    data serialization through orjson."""
    def __init__(self, client: WebSocketCommonProtocol) -> None:
        self.client = client

    async def send(self, message_type: str, **message_data) -> None:
        await self.client.send(orjson.dumps({"type": message_type, "data": message_data}))
