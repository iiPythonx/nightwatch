# Copyright (c) 2024 iiPython

# Modules
import anyio
import orjson
from pydantic import ValidationError

from starlette.requests import Request
from starlette.routing import Route, WebSocketRoute
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.websockets import WebSocket
from starlette.applications import Starlette

from .utils import broadcast
from .utils.commands import registry
from .utils.constant import Constant
from .utils.websocket import NightwatchClient

from nightwatch.logging import log

# Handle state
class NightwatchStateManager():
    def __init__(self) -> None:
        self.clients = {}

    def add_client(self, client: WebSocket) -> None:
        self.clients[client] = None

    def remove_client(self, client: WebSocket) -> None:
        if client in self.clients:
            del self.clients[client]

state = NightwatchStateManager()

# Handle API
async def route_home(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Nightwatch is running.")

async def route_info(request: Request) -> JSONResponse:
    return JSONResponse({
        "name": Constant.SERVER_NAME,
        "version": Constant.SERVER_VERSION,
        "icon": Constant.SERVER_ICON
    })

# Socket entrypoint
async def route_gateway(websocket: WebSocket) -> None:
    await websocket.accept()

    client = NightwatchClient(state, websocket)
    async with anyio.create_task_group() as task_group:
        async def run_chatroom_ws_receiver() -> None:
            await chatroom_ws_receiver(websocket, client)
            task_group.cancel_scope.cancel()

        task_group.start_soon(run_chatroom_ws_receiver)
        await chatroom_ws_sender(websocket)

async def chatroom_ws_receiver(websocket: WebSocket, client: NightwatchClient) -> None:
    try:
        async for message in websocket.iter_text():
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
                    await client.send("error", text = str(error))

    except orjson.JSONDecodeError:
        log.warn("ws", "Failed to decode JSON from client.")

    state.remove_client(websocket)
    log.info("ws", "Client disconnected.")

async def chatroom_ws_sender(websocket: WebSocket) -> None:
    async with broadcast.subscribe("general") as sub:
        async for event in sub:  # type: ignore
            await websocket.send_text(event.message)

app = Starlette(
    routes = [
        Route("/", route_home),
        Route("/info", route_info),
        WebSocketRoute("/gateway", route_gateway)
    ],
    on_startup = [broadcast.connect],
    on_shutdown = [broadcast.disconnect]
)
