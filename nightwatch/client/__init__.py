# Copyright (c) 2024 iiPython

# Modules
import asyncio
import websockets
from threading import Thread

from nightwatch import __version__
from nightwatch.config import config

from .extra.ui import ui
from .extra.select import menu
from .extra.wswrap import ORJSONWebSocket

# Connection handler
async def connect(host: str, port: int) -> None:
    destination = f"ws{'s' if port == 443 else ''}://{host}:{port}/gateway"
    try:
        async with websockets.connect(destination) as ws:
            ws = ORJSONWebSocket(ws)

            # Handle identification payload
            await ws.send({"type": "identify", "name": config["username"]})
            response = await ws.recv()
            if "error" in response:
                exit(f"\nCould not connect to {destination}. Additional details:\n{response['error']}")

            # Start the input thread
            Thread(target = asyncio.run, args = [ui.input_loop(ws)]).start()

            # Enter the mainloop
            ui.on_ready(response)
            while ws.ws:
                ui.on_message(await ws.recv())

    except websockets.exceptions.InvalidURI:
        exit(f"\nCould not connect to {destination} due to an HTTP redirect.\nPlease ensure you entered the correct address.")

    except OSError:
        exit(f"\nCould not connect to {destination} due to an OSError.\nThis is more then likely because the server is not running.")

# Entrypoint
def start_client(
    address: str = None,
    username: str = None
):
    username = username or config["username"]

    # Start main UI
    print(f"\033[H\033[2J✨ Nightwatch | v{__version__}\n")
    if username is None:
        print("Hello! It seems that this is your first time using Nightwatch.")
        print("Before you can connect to a server, please set your desired username.\n")
        config.set("username", input("Username: "))
        print("\033[4A\033[0J", end = "")  # Reset back up to the Nightwatch label

    # Handle server address
    if address is None:
        servers = config["servers"]
        if servers is None:
            servers = ["nightwatch.iipython.dev"]
            config.set("servers", servers)

        print(f"Hello, {config['username']}. Please select a Nightwatch server to connect to:")
        address = menu.show(servers)
        print()

    print(f"Establishing connection to {address} ...")

    # Parse said address
    if ":" not in address:
        host, port = address, 443

    else:
        host, port = address.split(":")

    # Connect to server
    asyncio.run(connect(host, port))
