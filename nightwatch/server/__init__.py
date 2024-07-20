# Copyright (c) 2024 iiPython

# Modules
from http import HTTPStatus

import orjson
from pydantic import ValidationError
from websockets import WebSocketCommonProtocol, Headers
from websockets.exceptions import ConnectionClosedError

from .utils.commands import registry
from .utils.constant import Constant
from .utils.websocket import NightwatchClient

from nightwatch.logging import log

# Handle state
class NightwatchStateManager():
    def __init__(self) -> None:
        self.clients = {}

    def add_client(self, client: WebSocketCommonProtocol) -> None:
        self.clients[client] = None

    def remove_client(self, client: WebSocketCommonProtocol) -> None:
        if client in self.clients:
            del self.clients[client]

state = NightwatchStateManager()

# Handle API
async def process_api(path: str, request_headers: Headers) -> tuple[HTTPStatus, list, bytes]:
    if path == "/info":
        return HTTPStatus.OK, [], orjson.dumps({
            "name": Constant.SERVER_NAME,
            "version": Constant.SERVER_VERSION,
            "icon": Constant.SERVER_ICON
        })

    return HTTPStatus.NOT_FOUND, [], b"Not Found\n"

# Socket entrypoint
async def connection(websocket: WebSocketCommonProtocol) -> None:
    try:
        client = NightwatchClient(state, websocket)
        async for message in websocket:
            message = orjson.loads(message)
            if message.get("type") not in registry.commands:
                await client.send("error", text = "Specified command type does not exist or is missing.")
                continue

            callback = message.get("callback")
            if callback is not None:
                client.set_callback(callback)

            command, payload_type = registry.commands[message["type"]]
            if payload_type is None:
                await command(state, client)

            else:
                try:
                    await command(state, client, payload_type(**(message.get("data") or {})))

                except ValidationError as error:
                    await client.send("error", text = error)

    except orjson.JSONDecodeError:
        log.warn("ws", "Failed to decode JSON from client.")

    except ConnectionClosedError:
        log.info("ws", "Client disconnected.")
    
    state.remove_client(websocket)
