# Copyright (c) 2024 iiPython

# Modules
import urwid
from datetime import datetime
from typing import Tuple
from types import FunctionType

from .commands import commands
from .wswrap import ORJSONWebSocket
from ..vendor.scroll import Scrollable, ScrollBar

# Input edit class
class InputEdit(urwid.Edit):
    def __init__(self, send_message: FunctionType) -> None:
        self.send_message = send_message
        super().__init__("> ", wrap = "clip")

    def keypress(self, size: Tuple[int], key: str) -> None:
        if key != "enter":
            return super().keypress(size, key)

        elif not self.edit_text.strip():
            return

        self.send_message(self.edit_text)
        self.edit_text = ""

# Main UI class
class NightwatchUI():
    def __init__(self, websocket: ORJSONWebSocket) -> None:
        self.last_author, self.last_time = None, 0
        self.websocket = websocket

        # Main urwid setup
        self.pile = urwid.Pile([])
        self.scroll = Scrollable(urwid.Filler(self.pile, valign = "top"))
        self.frame = urwid.Frame(ScrollBar(self.scroll), footer = InputEdit(self.send_message), focus_part = "footer")

        # Initialize commands
        self.commands = {}
        for command in commands:
            command = command(self.add_message)
            self.commands[command.name] = command

    def send_message(self, text: str) -> None:
        if text[0] == "/" and text[1:] in self.commands:
            response = self.commands[text[1:]].on_execute(text.split(" ")[1:])
            if response is not None:
                text = response

        self.websocket.send({"type": "message", "text": text})

    def construct_message(self, author: str, content: str) -> None:
        visible_author = author if author != self.last_author else " " * len(author)
        now, time_string = datetime.now(), ""
        if (author != self.last_author) or ((now - self.last_time).total_seconds() > 300):
            time_string = now.strftime("%I:%M %p") + "  "  # Right padding for the scrollbar

        self.pile.contents.append((urwid.Columns([
            (len(visible_author), urwid.Text(("yellow", visible_author))),
            (3, urwid.Text(("gray", " | "))),
            ("weight", 4, urwid.Text(content)),
            (len(time_string) + 2, urwid.Text(("green", time_string), align = "right"))  # +2 adds left padding
        ]), self.pile.options()))
        self.last_author, self.last_time = author, now

    def add_message(self, author: str, content: str) -> None:
        self.construct_message(author, content)

        # Scroll to the end (if we haven't manually moved)
        if len(self.pile.contents) > 50:
            self.pile.contents = self.pile.contents[1:]

        self.scroll.to_end()
        self.loop.screen.clear()
        self.loop.draw_screen()

    def on_message(self, data: dict) -> None:
        self.add_message(data.get("name", "Nightwatch"), data["text"])

    def on_ready(self, loop: urwid.MainLoop, payload: dict) -> None:
        self.loop = loop
        self.construct_message("Nightwatch", f"Welcome to {payload['name']}. There are {payload['online']} user(s) online.")
