# Copyright (c) 2024 iiPython

# Modules
from typing import Type
import orjson
from websockets import WebSocketCommonProtocol
from websockets.exceptions import ConnectionClosedError

from .utils.commands import registry
from .utils.websocket import NightwatchClient

from nightwatch.logging import log

# Handle state
class NightwatchStateManager():
    def __init__(self) -> None:
        self.clients = set()
        self.message_buffer = []

    def add_client(self, client: WebSocketCommonProtocol) -> None:
        print("Client registered")
        self.clients.add(client)

    def remove_client(self, client: WebSocketCommonProtocol) -> None:
        print("Client removed")
        self.clients.remove(client)

state = NightwatchStateManager()

# Socket entrypoint
async def connection(websocket: WebSocketCommonProtocol) -> None:
    try:
        state.add_client(websocket)

        client = NightwatchClient(websocket)
        async for message in websocket:
            message = orjson.loads(message)
            if message.get("type") not in registry.commands:
                await client.send("error", text = "Specified command type does not exist or is missing.")
                continue

            data = message.get("data") or {}
            missing_parameters = registry.types[message["type"]].keys() - data.keys()
            if missing_parameters:
                await client.send("error", text = f"The following parameters are missing: {', '.join(missing_parameters)}.")
                continue

            try:
                await registry.commands[message["type"]](state, client, *[
                    v(data[k])
                    for k, v in registry.types[message["type"]].items()
                ])

            except (TypeError, ValueError):
                await client.send("error", text = "Failed to convert your arguments to the appropriate datatype.")

    except orjson.JSONDecodeError:
        log.warn("ws", "Failed to decode JSON from client.")

    except ConnectionClosedError:
        log.info("ws", "Client disconnected.")
    
    state.remove_client(websocket)
