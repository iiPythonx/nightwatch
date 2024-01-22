# Copyright (c) 2024 iiPython

# Modules
from fastapi import FastAPI, WebSocket

from .patches import iter_binary_json, BrokenClient

from nightwatch import __version__
from nightwatch.config import config

# Initialization
print(f"✨ Nightwatch | v{__version__}")

server_name = config["server.name"] or "Untitled Server"
app = FastAPI(openapi_url = None)

# Manager class
class Manager():
    def __init__(self) -> None:
        self.connections = {}
        self.commands = {
            "message": (self._message, ["text"]),
            "identify": (self._identify, ["name"])
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

        elif not text.strip():
            return await ws.send_json({"text": "You cannot send an empty message."})

        elif len(text) > 300:
            return await ws.send_json({"text": "Message is too large, maximum limit is 300 characters."})

        await self.broadcast({"name": self.connections[ws], "text": text})

    async def _identify(self, ws: WebSocket, name: str) -> None:
        if not name.strip():
            return await ws.send_json({"text": "No username specified."})
        
        elif ws in self.connections:
            return await ws.send_json({"text": "You have already identified."})

        elif name in self.connections.values():
            return await ws.send_json({"text": "Specified username is already taken."})

        elif len(name) > 30:
            return await ws.send_json({"text": "Specified username is too large, maximum is 30 characters."})

        self.connections[ws] = name
        await ws.send_json({"online": len(self.connections), "name": server_name})

    async def handle_message(self, ws: WebSocket, message: dict) -> None:
        if "type" not in message:
            return await ws.close()

        elif message["type"] not in self.commands:
            return await ws.send_json({"text": "Specified type is invalid."})

        # Handle command
        args = []
        callback, arg_list = self.commands[message["type"]]
        for _ in arg_list:
            if _ not in message:
                return await ws.send_json({"text": f"Missing argument: '{_}'."})

            args.append(message[_])

        await callback(ws, *args)

manager = Manager()

# Handle websocket routing
@app.websocket("/gateway")
async def gateway_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        async for message in iter_binary_json(websocket):
            await manager.handle_message(websocket, message)

    except BrokenClient:
        pass

    # Clean up and free username
    if websocket in manager.connections:
        del manager.connections[websocket]
