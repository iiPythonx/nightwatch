# Copyright (c) 2024 iiPython

# Modules
from typing import List
from types import FunctionType

# Main class
class BaseCommand():
    def __init__(self, name: str, add_message: FunctionType) -> None:
        self.name = name
        self.add_message = add_message

    def print(self, message: str) -> None:
        self.add_message(self.name.title(), message)

# Commands
class ShrugCommand(BaseCommand):
    def __init__(self, *args) -> None:
        super().__init__("shrug", *args)

    def on_execute(self, args: List[str]) -> str:
        return "¯\_(ツ)_/¯"

commands = [
    ShrugCommand
]
