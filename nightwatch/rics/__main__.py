# Copyright (c) 2025 iiPython
# Launch the Nightwatch RICS through uvicorn, while disabling logging

# Modules
import os
import sys

import uvicorn

# Launch uvicorn
uvicorn.run(
    "nightwatch.rics:app",  # Allow debug reloading,
    host = os.getenv("HOST", "127.0.0.1"),
    port = int(os.getenv("PORT") or 8000),
    # log_level = "critical",  # Soon! when i have a better idea for logging requests
    reload = "--dev" in sys.argv
)
