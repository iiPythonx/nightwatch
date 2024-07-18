# Copyright (c) 2024 iiPython

# Modules
import os
import asyncio

from websockets.server import serve

from . import connection

from nightwatch import __version__
from nightwatch.logging import log

# Entrypoint
async def main() -> None:
    host, port = os.getenv("HOST", "localhost"), int(os.getenv("PORT", 8000))
    log.info("ws", f"Nightwatch v{__version__} running on ws://{host}:{port}/")
    async with serve(connection, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
