# Copyright (c) 2024 iiPython

# Modules
import os
from threading import Thread

import urwid
import websockets
from websockets.sync.client import connect

from nightwatch import __version__
from nightwatch.config import config

from .extra.ui import NightwatchUI
from .extra.select import menu
from .extra.wswrap import ORJSONWebSocket

# Initialization
if os.name == "nt":
    urwid.set_encoding("utf-8")

# Connection handler
def connect_loop(host: str, port: int) -> None:
    destination = f"ws{'s' if port == 443 else ''}://{host}:{port}/gateway"
    try:
        with connect(destination) as ws:
            ws = ORJSONWebSocket(ws)

            # Handle identification payload
            ws.send({"type": "identify", "name": config["user.name"], "color": config["user.color"]})
            response = ws.recv()
            if "text" in response:
                exit(f"\nCould not connect to {destination}. Additional details:\n{response['text']}")

            # Create UI
            ui = NightwatchUI(ws)
            loop = urwid.MainLoop(ui.frame, [
                ("yellow", "yellow", ""),
                ("gray", "dark gray", "", "", "#555753", ""),
                ("green", "dark green", "")
            ])
            loop.screen.set_terminal_properties(2 ** 24)  # Activate 24-bit color mode

            # Individual components
            loop.screen.register_palette_entry("time", "dark green", "", foreground_high = config["colors.time"] or "#00FF00")
            loop.screen.register_palette_entry("sep", "dark gray", "", foreground_high = config["colors.sep"] or "#555753")

            # Handle messages
            def message_loop(ws: ORJSONWebSocket, ui: NightwatchUI) -> None:
                try:
                    while ws.ws:
                        ui.on_message(ws.recv())

                except websockets.exceptions.ConnectionClosed:
                    return

            Thread(target = message_loop, args = [ws, ui]).start()

            # Start mainloop
            ui.on_ready(loop, response)
            loop.run()

    except websockets.exceptions.InvalidURI:
        exit(f"\nCould not connect to {destination} due to an HTTP redirect.\nPlease ensure you entered the correct address.")

    except OSError:
        exit(f"\nCould not connect to {destination} due to an OSError.\nThis is more then likely because the server is not running.")

# Entrypoint
def start_client(
    address: str = None,
    username: str = None
):
    username = username or config["user.name"]

    # Start main UI
    print(f"\033[H\033[2J✨ Nightwatch | v{__version__}\n")
    if username is None:
        print("Hello! It seems that this is your first time using Nightwatch.")
        print("Before you can connect to a server, please set your desired username.\n")
        config.set("user.name", input("Username: "))
        print("\033[4A\033[0J", end = "")  # Reset back up to the Nightwatch label

    # Handle server address
    if address is None:
        servers = config["servers"]
        if servers is None:
            servers = ["nightwatch.iipython.dev"]
            config.set("servers", servers)

        print(f"Hello, {config['user.name']}. Please select a Nightwatch server to connect to:")
        address = menu.show(servers)
        print()

    print(f"Establishing connection to {address} ...")

    # Parse said address
    if ":" not in address:
        host, port = address, 443

    else:
        host, port = address.split(":")

    # Connect to server
    try:
        connect_loop(host, port)

    except KeyboardInterrupt:
        print("\033[5A\033[0J", end = "")  # Reset back up to the Nightwatch label
        print(f"Goodbye, {config['user.name']}.")
