# Copyright (c) 2024 iiPython

# Modules
import ujson
from nanoid import generate
from socketify import App, OpCode, CompressOptions

from nightwatch import __version__
from .core import nightwatch, commands, construct

# Session class
class Session():
    def __init__(self, ws, callback: str = None) -> None:
        self.ws, self.callback = ws, callback
        self.publish = self.ws.publish

        # Handy attributes
        self.id = self.ws.get_user_data()["id"]

    def send(self, data: dict) -> None:
        if self.callback is not None:
            data["callback"] = self.callback

        self.ws.send(data, OpCode.TEXT)

# Initialization
def ws_open(ws) -> None:
    ws.subscribe("general")

def ws_message(ws, message, opcode) -> None:
    try:
        data = ujson.loads(message)
        ws = Session(ws, data.get("callback"))
        if data.get("type") not in commands:
            return ws.send(construct("error", text = "Specified type is invalid."))
    
        command, data, payload = commands[data["type"]], data.get("data", {}), []
        for k, t in command.__annotations__.items():
            if k == "return":
                continue

            elif k not in data:
                return ws.send(construct("error", text = f"Missing argument: '{k}'."))

            payload.append(t(data[k]))

        command(nightwatch, ws, *payload)

    except ValueError:
        ws.send(construct("error", text = "Failed to convert your argument to a valid datatype."))

    except ujson.JSONDecodeError:
        pass

def ws_close(ws, code, message) -> None:
    user_id = ws.get_user_data()["id"]
    if user_id in nightwatch.connections:
        del nightwatch.connections[user_id]

def ws_upgrade(res, req, socket_context):
    res.upgrade(
        req.get_header("sec-websocket-key"),
        req.get_header("sec-websocket-protocol"),
        req.get_header("sec-websocket-extensions"),
        socket_context,
        {"id": generate()}
    )

# Initialization
app = App()
app.ws(
    "/gateway",
    {
        "compression": CompressOptions.SHARED_COMPRESSOR,
        "max_payload_length": 64 * 1024,
        "idle_timeout": 960,
        "open": ws_open,
        "message": ws_message,
        "upgrade": ws_upgrade,
        "close": ws_close,
    }
)
app.listen(
    8080,
    lambda config: print(f"✨ Nightwatch | v{__version__}\nListening on port http://localhost:{config.port} now\n")
)
app.run()
