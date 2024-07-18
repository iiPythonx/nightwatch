# Copyright (c) 2024 iiPython

# Modules
from typing import Any

import orjson
from websockets import WebSocketCommonProtocol

class NightwatchClient():
    """This class acts as a wrapper on top of WebSocketCommonProtocol that implements
    data serialization through orjson."""
    def __init__(self, state, client: WebSocketCommonProtocol) -> None:
        self.client = client
        self.identified, self.callback = False, None

        self.state = state
        self.state.add_client(client)

    async def send(self, message_type: str, **message_data) -> None:
        payload = {"type": message_type, "data": message_data}
        if self.callback is not None:
            payload["callback"] = self.callback
            self.callback = None

        await self.client.send(orjson.dumps(payload).decode())

    def set_callback(self, callback: str) -> None:
        self.callback = callback

    # Handle user data (ie. name and color)
    def set_user_data(self, data: dict[str, Any]) -> None:
        self.user_data = data
        self.state.clients[self.client] = data["name"]
