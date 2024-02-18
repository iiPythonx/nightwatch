# Copyright (c) 2024 iiPython

# Modules
import re
from typing import Union

from socketify import OpCode

from nightwatch.config import config

# Handle checks
def perform_checks(checks: list) -> Union[str, None]:
    for check in checks:
        if check[0]():
            return check[1]

# Constants
hex_regex = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
server_user = {"name": "Nightwatch", "color": "gray"}
server_name = config["server.name"] or "Untitled Server"

def construct(type: str, **kwargs) -> dict:
    return {"type": type, "data": kwargs}

# Main methods
class NightwatchCore():
    def __init__(self) -> None:
        self.connections = {}

nightwatch = NightwatchCore()

# Handle command initialization
class CommandList:
    commands = {}

cmdlist = CommandList()

def command(func) -> None:
    cmdlist.commands[func.__name__] = func

# Commands
@command
def identify(self, ws, name: str, color: str) -> None:
    error = perform_checks([
        (lambda: color and not re.search(hex_regex, color), "Specified user color is not a valid HEX code."),
        (lambda: not name.strip(), "No username specified."),
        (lambda: name.lower() in ["nightwatch", "admin", "administrator", "moderator"], "Specified username is reserved."),
        (lambda: ws.id in self.connections, "You have already identified."),
        (lambda: name in [u["name"] for u in self.connections.values()], "Specified username is already taken."),
        (lambda: len(name) > 30, "Specified username is too large. Maximum is 30 characters.")
    ])
    if error is not None:
        return ws.send(construct("error", text = error))

    ws.send(construct("server", name = server_name, online = len(self.connections)))
    ws.publish(
        "general",
        construct("message", text = f"{name} joined the chatroom.", user = server_user),
        OpCode.TEXT
    )

    self.connections[ws.id] = {"name": name, "color": color}

@command
def message(self, ws, text: str) -> None:
    error = perform_checks([
        (lambda: ws.id not in self.connections, "You must identify before sending a message."),
        (lambda: not text.strip(), "You cannot send an empty message."),
        (lambda: len(text) > 300, "Message is too large, maximum limit is 300 characters.")
    ])
    if error is not None:
        return ws.send(construct("error", text = error))

    ws.publish(
        "general",
        construct("message", text = text, user = self.connections[ws.id]),
        OpCode.TEXT
    )

@command
def members(self, ws) -> None:
    ws.send(construct("members", list = [u["name"] for u in self.connections.values()]))

commands = cmdlist.commands
