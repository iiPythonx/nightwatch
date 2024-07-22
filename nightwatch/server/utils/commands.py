# Copyright (c) 2024 iiPython

# Modules
import json
from typing import Callable

import httpx
import orjson
from pydantic import HttpUrl, ValidationError

from . import models, broadcast
from .constant import Constant
from .websocket import NightwatchClient

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

registry, http_client = CommandRegistry(), httpx.AsyncClient()

# Setup commands
@registry.command("identify")
async def command_identify(state, client: NightwatchClient, data: models.IdentifyModel) -> None:
    if client.identified:
        return await client.send("error", text = "You have already identified.")

    # Fetch user data
    try:
        result = (await http_client.post(f"https://{data.auth_server.host}/api/profile", json = {
            "token": data.token.get_secret_value()
        })).json()
        if result["code"] != 200:
            return await client.send("error", text = "Auth server responded with non-200.")

        result = result["data"]

        # Using HttpUrl isn't "correct" but it works so ¯\_(ツ)_/¯
        username, domain = result["username"], HttpUrl(f"https://{result.get('domain') or data.auth_server.host}").host  # type: ignore
        if len(username) not in range(4, 36):  # Enforce same limits as auth server
            raise ValidationError

    except httpx.HTTPError:
        return await client.send("error", text = "Connection to auth server failed.")

    except (json.JSONDecodeError, KeyError, ValidationError):
        return await client.send("error", text = "Auth server did not respond properly.")

    # Check ownership of domain
    if domain != data.auth_server.host:
        try:
            result = (await http_client.get(f"https://{domain}/.well-known/nightwatch")).text
            if result != data.auth_server.host:
                return await client.send("error", text = "Custom domain does not have valid well-known file.")

        except httpx.HTTPError:
            return await client.send("error", text = "Failed to connect to domain for well-known check.")

    # Handle user data
    user_data = {"username": username, "domain": domain, "id": f"{username}:{domain}"}
    if user_data["id"] in state.clients.values():
        return await client.send("error", text = "You have already identified.")

    client.set_user_data(user_data)
    client.identified = True

    await client.send("server", name = Constant.SERVER_NAME, online = len(state.clients))
    await broadcast.publish("general", orjson.dumps({
        "type": "message",
        "data": {"text": f"@{user_data['id']} joined the chatroom.", "user": Constant.SERVER_USER}
    }).decode())

@registry.command("message")
async def command_message(state, client: NightwatchClient, data: models.MessageModel) -> None:
    if not client.identified:
        return await client.send("error", text = "You must identify before sending a message.")

    await broadcast.publish("general", orjson.dumps({
        "type": "message",
        "data": {"text": data.text, "user": client.user_data}
    }).decode())

@registry.command("members")
async def command_members(state, client: NightwatchClient) -> None:
    return await client.send("members", list = list(state.clients.values()))

@registry.command("ping")
async def command_ping(state, client: NightwatchClient) -> None:
    return await client.send("pong")
