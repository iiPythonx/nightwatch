# Copyright (c) 2024 iiPython

# Modules
import re
from fastapi import FastAPI, WebSocket

from .patches import iter_binary_json, BrokenClient

from nightwatch import __version__
from nightwatch.config import config

# Initialization
print(f"✨ Nightwatch | v{__version__}")

app = FastAPI(openapi_url = None)

# Constants
server_name = config["server.name"] or "Untitled Server"
hex_regex = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")

# Manager class
class Manager():
    def __init__(self) -> None:
        self.connections = {}
        self.commands = {
            "message": (self._message, ["text"], []),
            "identify": (self._identify, ["name", "color"], ["color"]),
            "members": (self._members, [], [])
        }
    
    async def broadcast(self, data: dict) -> None:
        for conn in self.connections:
            try:
                await conn.send_json(data)

            except Exception:
                await conn.close()

    async def _message(self, ws: WebSocket, text: str) -> None:
        if ws not in self.connections:
            return await ws.send_json({"text": "You must identify before sending a message."})

        text = str(text)
        if not text.strip():
            return await ws.send_json({"text": "You cannot send an empty message."})

        elif len(text) > 300:
            return await ws.send_json({"text": "Message is too large, maximum limit is 300 characters."})

        user = self.connections[ws]
        await self.broadcast({"user": user, "text": text})

    async def _identify(self, ws: WebSocket, name: str, color: str) -> None:
        color = str(color or "")
        for check in [
            (lambda: color and not re.search(hex_regex, color), "Specified user color is not a valid HEX code."),
            (lambda: not name.strip(), "No username specified."),
            (lambda: name.lower() in ["nightwatch", "admin", "administrator", "moderator"], "Specified username is reserved."),
            (lambda: ws in self.connections, "You have already identified."),
            (lambda: name in [u["name"] for u in self.connections.values()], "Specified username is already taken."),
            (lambda: len(name) > 30, "Specified username is too large. Maximum is 30 characters.")
        ]:
            if check[0]():
                return await ws.send_json({"text": check[1]})

        self.connections[ws] = {"name": name, "color": color or "yellow"}
        await ws.send_json({"online": len(self.connections), "name": server_name})
        await self.broadcast({"text": f"{name} joined the chatroom."})

    async def _members(self, ws: WebSocket) -> None:
        await ws.send_json({"members": [u["name"] for u in self.connections.values()]})

    async def handle_message(self, ws: WebSocket, message: dict) -> None:
        if "type" not in message:
            return await ws.close()

        elif message["type"] not in self.commands:
            return await ws.send_json({"text": "Specified type is invalid."})

        # Handle command
        if "callback" in message:
            setattr(ws, "callback", message["callback"])

        args = []
        callback, arg_list, optional = self.commands[message["type"]]
        for _ in arg_list:
            if _ not in message and _ not in optional:
                return await ws.send_json({"text": f"Missing argument: '{_}'."})

            args.append(message.get(_, None))

        await callback(ws, *args)

manager = Manager()

# Custom websocket wrapper
class Websocket():
    def __init__(self, ws: WebSocket) -> None:
        self.ws, self.callback = ws, None
        self.receive_json = self.ws.receive_json

    async def send_json(self, data: dict) -> None:
        if self.callback is not None:
            data["callback"] = self.callback

        self.callback = None
        return await self.ws.send_json(data)

# Handle websocket routing
@app.websocket("/gateway")
async def gateway_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    # Main loop
    try:
        websocket = Websocket(websocket)
        async for message in iter_binary_json(websocket):
            await manager.handle_message(websocket, message)

    except BrokenClient:
        pass

    # Clean up and free username
    if websocket in manager.connections:
        del manager.connections[websocket]
