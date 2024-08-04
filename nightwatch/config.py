# Copyright (c) 2024 iiPython

# Modules
import os
import json
import typing
from pathlib import Path

# Configuration class
class Configuration():
    def __init__(self) -> None:
        self.config_path = Path.home() / ("AppData/Local/Nightwatch/config.json" if os.name == "nt" else ".config/nightwatch/config.json")
        self.config_path.parent.mkdir(exist_ok = True)
        self.config = json.loads(self.config_path.read_text()) if self.config_path.is_file() else {}

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
        self.config_path.write_text(json.dumps(self.config, indent = 4))

config = Configuration()
