# Copyright (c) 2024 iiPython

# Modules
import os

import uvicorn

from . import app

from nightwatch import __version__
from nightwatch.logging import log

# Entrypoint
def main() -> None:
    host, port = os.getenv("HOST", "localhost"), int(os.getenv("PORT", 8000))
    log.info("ws", f"Nightwatch v{__version__} running on ws://{host}:{port}/")
    uvicorn.run(app, host = host, port = port, log_level = "info")

if __name__ == "__main__":
    main()
