# Copyright (c) 2024 iiPython

# Modules
from typing import Callable

import orjson
import websockets

from . import models
from .websocket import NightwatchClient

from nightwatch.config import config

# Constants
class Constant:
    SERVER_USER: dict[str, str] = {"name": "Nightwatch", "color": "gray"}
    SERVER_NAME: str = config["server.name"] or "Untitled Server"

# Handle command registration
class CommandRegistry():
    def __init__(self) -> None:
        self.commands = {}

    def command(self, name: str) -> Callable:
        def callback(function: Callable) -> None:
            self.commands[name] = (
                function,
                function.__annotations__["data"] if "data" in function.__annotations__ else None
            )

        return callback

registry = CommandRegistry()

# Setup commands
@registry.command("identify")
async def command_identify(state, client: NightwatchClient, data: models.IdentifyModel) -> None:
    if client.identified:
        return await client.send("error", text = "You have already identified.")

    elif data.name.lower() in ["nightwatch", "admin", "administrator", "moderator"]:
        return await client.send("error", text = "The specified username is reserved.")

    elif data.name in state.clients.values():
        return await client.send("error", text = "Specified username is already taken.")

    client.set_user_data(data.model_dump())
    client.identified = True

    await client.send("server", name = Constant.SERVER_NAME, online = len(state.clients))
    websockets.broadcast(state.clients, orjson.dumps({
        "type": "message",
        "data": {"text": f"{data.name} joined the chatroom.", "user": Constant.SERVER_USER}
    }).decode())

@registry.command("message")
async def command_message(state, client: NightwatchClient, data: models.MessageModel) -> None:
    if not client.identified:
        return await client.send("error", text = "You must identify before sending a message.")

    websockets.broadcast(state.clients, orjson.dumps({
        "type": "message",
        "data": {"text": data.text, "user": client.user_data}
    }).decode())

@registry.command("members")
async def command_members(state, client: NightwatchClient) -> None:
    return await client.send("members", list = list(state.clients.values()))

@registry.command("ping")
async def command_ping(state, client: NightwatchClient) -> None:
    return await client.send("pong")
