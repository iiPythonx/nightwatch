# Copyright (c) 2024 iiPython

# Modules
import typing
from time import time
from json import JSONDecodeError
from secrets import token_urlsafe

from pydantic import BaseModel, Field

from requests import Session
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect, WebSocketState

from nightwatch import __version__
from nightwatch.logging import log
from nightwatch.config import fetch_config

# Load config data
config = fetch_config("rics")

# Initialization
app = FastAPI(openapi_url = None)
app.add_middleware(CORSMiddleware, allow_origins = ["*"], allow_methods = ["*"])

session = Session()

# Check for updates
app.state.latest_update = None
if config["enable_update_checking"] is not False:
    latest = session.get("https://api.github.com/repos/iiPythonx/nightwatch/releases/latest").json()

    def version(v: str) -> tuple:
        return tuple(map(int, v.split(".")))

    if version(latest["name"][1:]) > version(__version__):
        log.info("update", f"Nightwatch {latest['name']} is now available, upgrading is recommended.")
        log.info("update", f"See the changelog at {latest['html_url']}.")
        app.state.latest_update = latest["name"][1:]

# Scaffold the application
app.state.clients = {}
app.state.pending_clients = {}
app.state.message_log = []

async def broadcast(payload: dict) -> None:
    payload["data"]["time"] = round(time())
    if payload["type"] == "message":
        if "user" not in payload["data"]:
            payload["data"]["user"] = {"name": "Nightwatch", "hex": "555753", "admin": False, "bot": True}

        app.state.message_log = app.state.message_log[-24:] + [payload["data"]]

    for client in app.state.clients.values():
        await client.send(payload)

app.state.broadcast = broadcast

# Setup routing
class Client:
    def __init__(self, websocket: WebSocket, user_data: dict[str, typing.Any]) -> None:
        self.websocket = websocket
        self.username, self.hex_code = user_data["username"], user_data["hex"]

        # Attributes
        self.admin, self.bot = False, user_data["bot"]

        # Attach to client list
        self._callback = None
        app.state.clients[self.username] = self

    def serialize(self) -> dict[str, str | bool]:
        return {"name": self.username, "hex": self.hex_code, "admin": self.admin, "bot": self.bot}

    def cleanup(self) -> None:
        del app.state.clients[self.username]
        del self  # Not sure if this helps, in case Python doesn't GC

    async def send(self, payload: dict) -> None:
        if self.websocket.application_state != WebSocketState.CONNECTED:
            return

        try:
            if self._callback is not None and payload["type"] != "message":
                payload["data"] = payload.get("data", {}) | {"callback": self._callback}
                self._callback = None

            await self.websocket.send_json(payload)

        except WebSocketDisconnect:
            pass

    async def receive(self) -> typing.Any:
        try:
            data = await self.websocket.receive_json()

            # Handle callback
            callback = data.get("data", {}).get("callback")
            if isinstance(callback, str):
                self._callback = callback

            return data

        except KeyError:
            await self.websocket.close(1002, "Nightwatch uses text frames, binary frames are rejected.")

        except JSONDecodeError:
            await self.websocket.close(1002, "Nightwatch requires all packets to be sent using JSON, non-JSON is rejected.")

        except WebSocketDisconnect:
            pass

        except Exception:
            await self.websocket.close(1002, "Some data parsing issue occured, check your payloads.")

        return None

class ClientJoinModel(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 30)
    hex: str = Field(..., min_length = 6, max_length = 6, pattern = "^[0-9A-Fa-f]{6}$")
    bot: bool = False

@app.post("/api/join")
async def route_index(client: ClientJoinModel) -> JSONResponse:
    if client.username in app.state.clients:
        return JSONResponse({
            "code": 400,
            "message": "Requested username is in use on this server."
        }, status_code = 400)

    if client.username.strip() != client.username:
        return JSONResponse({
            "code": 400,
            "message": "Requested username has whitespace that should be removed prior to joining."
        }, status_code = 400)

    if client.username.lower() in ["nightwatch", "admin", "moderator"]:
        return JSONResponse({
            "code": 400,
            "message": "Requested username is restricted for use."
        }, status_code = 400)

    client_token = token_urlsafe()
    app.state.pending_clients[client_token] = client.model_dump()
    return JSONResponse({
        "code": 200,
        "authorization": client_token
    })

@app.websocket("/api/ws")
async def connect_endpoint(
    authorization: str,
    websocket: WebSocket
) -> None:
    if authorization not in app.state.pending_clients:
        return await websocket.close(1008)

    user_data = app.state.pending_clients[authorization]
    del app.state.pending_clients[authorization]

    await websocket.accept()

    # Initialize client
    client = Client(websocket, user_data)

    # Get the client up to speed
    await client.send({"type": "rics-info", "data": {
        "name": config["name"] or "Nightwatch Server",
        "message-log": app.state.message_log,
        "user-list": [client.serialize() for client in app.state.clients.values()]
    }})

    # Broadcast join
    await app.state.broadcast({"type": "join", "data": {"user": client.serialize()}})
    await app.state.broadcast({"type": "message", "data": {"message": f"{client.username} has joined the server."}})

    # Handle loop
    while websocket.application_state == WebSocketState.CONNECTED:
        match await client.receive():
            case {"type": "message", "data": {"message": message}}:
                if not message.strip():
                    await client.send({"type": "problem", "data": {"message": "You cannot send a blank message."}})
                    continue

                await app.state.broadcast({"type": "message", "data": {"user": client.serialize(), "message": message}})
                if client._callback is not None:
                    await client.send({"type": "response"})

            case {"type": "user-list", "data": _}:
                await client.send({"type": "response", "data": {
                    "user-list": [client.serialize() for client in app.state.clients.values()]
                }})

            case None:
                break

            case _:
                await client.send({"type": "problem", "data": {"message": "Invalid payload received."}})

    client.cleanup()
    await app.state.broadcast({"type": "leave", "data": {"user": client.serialize()}})
    await app.state.broadcast({"type": "message", "data": {"message": f"{client.username} has left the server."}})

@app.get("/api/version")
async def route_version() -> JSONResponse:
    return JSONResponse({"code": 200, "data": {"version": __version__, "latest": app.state.latest_update}})

# Load additional routes
from nightwatch.rics.routing import (  # noqa: E402
    files,          # noqa: F401
    image_forward   # noqa: F401
)
