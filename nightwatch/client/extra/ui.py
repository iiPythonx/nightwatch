# Copyright (c) 2024 iiPython

# Modules
import os
import sys
import atexit
from datetime import datetime
from websockets import WebSocketCommonProtocol

from .iipython.iikp import readchar, keys

# Main UI class
class NightwatchUI():
    def __init__(self) -> None:
        self.last_author, self.last_time = None, 0
        self.input_text, self.message_buffer = "", []

        # This is set each time a message is received
        # Just here so we have the terminal size for the Nightwatch message
        self._ts = os.get_terminal_size()

    def add_message(self, author: str, content: str) -> None:
        message = f"{author if author != self.last_author else ' ' * len(author)} | {content}"

        # Calculate the time string
        now, time_string = datetime.now(), ""
        if (author != self.last_author) or ((now - self.last_time).total_seconds() > 300):
            formatted_time = now.strftime("%I:%M %p")
            time_string = (" " * (self._ts[0] - len(message) - len(formatted_time))) + formatted_time

        self.last_author, self.last_time = author, now
        self.message_buffer.append(f"{message}{time_string}")
        print(self.message_buffer[-1])

    def on_ready(self, payload: dict) -> None:
        sys.stdout.write("\033[H\033[2J\033[?25l")
        self.add_message("Nightwatch", f"Welcome to {payload['name']}. There are {payload['online']} user(s) online.")

    def on_message(self, data: dict) -> None:
        self._ts = os.get_terminal_size()

        # Handle message buffering
        buffer_length = len(self.message_buffer)
        sys.stdout.write(f"\033[{buffer_length + 1};0H\033[2K")
        if buffer_length >= self._ts[1] - 3:
            self.message_buffer = self.message_buffer[1:]

            # Rebuffer everything
            sys.stdout.write("\033[1J\033[H")
            print(*[f"\033[2K\033[1G{m}" for m in self.message_buffer], sep = "\n")
            sys.stdout.write("\033[2K\033[1G")  # For the next line

        self.add_message(data["name"], data["text"])
        self.write_input_field()

    def write_input_field(self) -> None:
        sys.stdout.write(f"\033[{self._ts[1]};0H\033[2K> {self.input_text}_\r")
        sys.stdout.flush()

    async def input_loop(self, ws: WebSocketCommonProtocol) -> None:
        while True:
            self.write_input_field()

            # Read characters
            kp = readchar()
            if isinstance(kp, str):
                self.input_text += kp

            elif kp == keys.BACKSPACE and self.input_text:
                self.input_text = self.input_text[:-1]

            elif kp == keys.ENTER and self.input_text:
                await ws.send({"type": "message", "text": self.input_text})
                self.input_text = ""

            elif kp == keys.CTRL_C:
                break

        sys.exit(0)

ui = NightwatchUI()

# Fix cursor on exit
atexit.register(lambda: print("\033[?25h"))
