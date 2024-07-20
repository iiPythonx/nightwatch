# Copyright (c) 2024 iiPython

# Modules
from typing import Any

import orjson
from starlette.websockets import WebSocket

class NightwatchClient():
    """This class acts as a wrapper on top of WebSocket that implements
    data serialization through orjson."""
    def __init__(self, state, client: WebSocket) -> None:
        self.client = client
        self.identified, self.callback = False, None

        self.state = state
        self.state.add_client(client)

    async def send(self, message_type: str, **message_data) -> None:
        payload = {"type": message_type, "data": message_data}
        if self.callback is not None:
            payload["callback"] = self.callback
            self.callback = None

        await self.client.send_text(orjson.dumps(payload).decode())

    def set_callback(self, callback: str) -> None:
        self.callback = callback

    # Handle user data (ie. name and color)
    def set_user_data(self, data: dict[str, Any]) -> None:
        self.user_data = data
        self.state.clients[self.client] = data["name"]
