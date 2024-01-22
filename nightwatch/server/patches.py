# Copyright (c) 2024 iiPython

# Modules
import json
import typing

from fastapi import WebSocket, WebSocketDisconnect

# Exceptions
class BrokenClient(Exception):
    pass

# iter_json but with mode set to binary
async def iter_binary_json(websocket: WebSocket) -> typing.AsyncIterator[typing.Any]:
    try:
        while True:
            yield await websocket.receive_json(mode = "binary")

    except WebSocketDisconnect:
        pass

    except (KeyError, json.JSONDecodeError):
        raise BrokenClient