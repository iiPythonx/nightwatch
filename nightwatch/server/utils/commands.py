# Copyright (c) 2024 iiPython

# Modules
from typing import Callable

from . import models
from .websocket import NightwatchClient

# Handle command registration
class CommandRegistry():
    def __init__(self) -> None:
        self.commands = {}

    def command(self, name: str) -> Callable:
        def callback(function: Callable) -> None:
            self.commands[name] = (function, function.__annotations__["data"])

        return callback

registry = CommandRegistry()

# Setup commands
@registry.command("identify")
async def command_identify(state, client: NightwatchClient, data: models.IdentifyModel) -> None:
    print(data)
