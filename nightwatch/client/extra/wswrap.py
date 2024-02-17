# Copyright (c) 2024 iiPython

# Modules
import orjson
from nanoid import generate
from types import FunctionType
from websockets import WebSocketCommonProtocol

# Main class
class ORJSONWebSocket():
    def __init__(self, ws: WebSocketCommonProtocol) -> None:
        self.ws = ws
        self.callbacks = {}

    def recv(self) -> dict:
        return orjson.loads(self.ws.recv())

    def send(self, data: dict) -> None:
        self.ws.send(orjson.dumps(data).decode())

    def callback(self, payload: dict, callback: FunctionType) -> None:
        callback_id = generate()
        self.callbacks[callback_id] = callback
        self.send(payload | {"callback": callback_id})
