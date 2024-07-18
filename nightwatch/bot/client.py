# Copyright (c) 2024 iiPython

# Modules
import asyncio
from typing import Awaitable

import orjson
from websockets import connect, WebSocketCommonProtocol

from .types import User, Message

# Main client class
class Client():
    def __init__(self, address: str) -> None:
        address = address.split(":")
        self.host, self.port = address[0], 443 if len(address) == 1 else int(address[1])

        # Event connections
        self._connected, self._on_message = None, None

    # Main event loop
    async def _loop(self, ws: WebSocketCommonProtocol) -> None:
        while ws:
            payload = orjson.loads(await ws.recv())
            data = payload.get("data", {})

            # Handle all the different types
            match payload["type"]:
                case "message":
                    if self._on_message is not None:
                        await self._on_message(Message(User(*data["user"].values()), data["text"]))

    async def connect(self) -> None:
        async with connect(f"ws{'s' if self.port == 443 else ''}://{self.host}:{self.port}/gateway") as ws:
            if self._connected is not None:
                await self._connected()

            await self._loop(ws)

    def run(self) -> None:
        asyncio.run(self.connect())

    # Handle event connections
    def connected(self, func: Awaitable) -> None:
        self._connected = func

    def on_message(self, func: Awaitable) -> None:
        self._on_message = func
