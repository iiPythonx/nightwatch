# Copyright (c) 2024 iiPython

# Modules
from typing import List
from types import FunctionType

from nightwatch import __version__
from nightwatch.config import config

# Main class
class BaseCommand():
    def __init__(self, name: str, ui, add_message: FunctionType) -> None:
        self.name, self.ui = name, ui
        self.add_message = add_message

    def print(self, message: str) -> None:
        self.add_message(self.name.title(), message)

# Commands
class ShrugCommand(BaseCommand):
    def __init__(self, *args) -> None:
        super().__init__("shrug", *args)

    def on_execute(self, args: List[str]) -> str:
        return "¯\_(ツ)_/¯"

class ConfigCommand(BaseCommand):
    def __init__(self, *args) -> None:
        super().__init__("config", *args)

    def on_execute(self, args: List[str]) -> None:
        if not args:
            for line in [
                "Nightwatch client configuration",
                "Usage: /config <key> <value>",
                "",
                "Example usage:",
                "/config colors.time yellow",
                "/config prompt \">> \"",
                "",
                "Some changes will only apply after Nightwatch restarts."
            ]:
                self.print(line)

            return

        elif len(args) < 2:
            return self.print(f"Missing the value to assign to '{args[0]}'.")

        config.set(args[0], args[1])
        self.print(f"{args[0]} has been set to \"{args[1]}\".")

class HelpCommand(BaseCommand):
    def __init__(self, *args) -> None:
        super().__init__("help", *args)

    def on_execute(self, args: List[str]) -> None:
        self.print(f"✨ Nightwatch v{__version__}")
        self.print("Available commands:")
        for command in self.ui.commands:
            self.print(f"  /{command}")

class MembersCommand(BaseCommand):
    def __init__(self, *args) -> None:
        super().__init__("members", *args)

    def on_execute(self, args: List[str]) -> None:
        def members_callback(response: dict):
            self.print(", ".join(response["members"]))

        self.ui.websocket.callback({"type": "members"}, members_callback)

commands = [
    ShrugCommand,
    ConfigCommand,
    HelpCommand,
    MembersCommand
]
