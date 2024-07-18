# Copyright (c) 2024 iiPython

# Modules
from typing import Callable

# Handle command registration
class CommandRegistry():
    def __init__(self) -> None:
        self.types, self.commands = {}, {}

    def command(self, name: str) -> Callable:
        def callback(function: Callable) -> None:
            self.types[name] = {
                k: v for k, v in function.__annotations__.items()
                if k not in ["state", "client", "return"]
            }
            self.commands[name] = function

        return callback

registry = CommandRegistry()

# Setup commands
@registry.command("identify")
async def command_identify(state, client, name: str, color: int) -> None:
    print(state, client, name, color)
