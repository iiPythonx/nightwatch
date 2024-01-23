# Copyright (c) 2024 iiPython

# Modules
import orjson
from websockets import WebSocketCommonProtocol

# Main class
class ORJSONWebSocket():
    def __init__(self, ws: WebSocketCommonProtocol) -> None:
        self.ws = ws

    def recv(self) -> dict:
        return orjson.loads(self.ws.recv())

    def send(self, data: dict) -> None:
        self.ws.send(orjson.dumps(data))
