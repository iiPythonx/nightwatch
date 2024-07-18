# Copyright (c) 2024 iiPython

# Modules
import asyncio

from websockets.server import serve

from . import connection

# Entrypoint
async def main() -> None:
    async with serve(connection, "localhost", 8000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
