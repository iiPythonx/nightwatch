# Copyright (c) 2024 iiPython

# Modules
from nightwatch import __version__
from nightwatch.config import config

# Constants
class Constant:
    SERVER_USER: dict[str, str | None] = {"username": "Nightwatch", "domain": None, "id": "nightwatch"}
    SERVER_NAME: str = config["server.name"] or "Untitled Server"
    SERVER_ICON: str | None = config["server.icon_url"]
    SERVER_VERSION: str = __version__
