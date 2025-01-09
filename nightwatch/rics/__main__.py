# Copyright (c) 2025 iiPython
# Launch the Nightwatch RICS through uvicorn, while disabling logging

# Modules
import os
import sys

import uvicorn
from nightwatch.logging import log

# Launch uvicorn
host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT") or 8000)
log.info("http", f"Running on {host}:{port}!")

uvicorn.run(
    "nightwatch.rics:app",  # Allow debug reloading,
    host = host,
    port = port,
    log_level = "critical",
    reload = "--dev" in sys.argv
)
