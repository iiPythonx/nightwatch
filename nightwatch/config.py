# Copyright (c) 2024 iiPython

# Modules
import os
import json
import typing
from pathlib import Path
from getpass import getuser

# Initialization
config_path = Path(os.path.expanduser("~")) / ".config/nightwatch/config.json"
if os.name == "nt":
    config_path = Path(f"C:\\Users\\{getuser()}\\AppData\\Local\\Nightwatch\\config.json")

config_path.parent.mkdir(exist_ok = True)

# Configuration class
class Configuration():
    def __init__(self, config_path: Path) -> None:
        self.config, self.config_path = {}, config_path
        if config_path.is_file():
            with config_path.open() as fh:
                self.config = json.loads(fh.read())

    def __getitem__(self, item: str) -> typing.Any:
        v = self.config
        for k in item.split("."):
            if k not in v:
                return None

            v = v[k]

        return v

    def set(self, key: str, value: typing.Any) -> None:
        v = self.config
        for k in key.split(".")[:-1]:
            if k not in v:
                v[k] = {}

            v = v[k]

        v[key.split(".")[-1]] = value
        with self.config_path.open("w+") as fh:
            fh.write(json.dumps(self.config, indent = 4))

config = Configuration(config_path)
