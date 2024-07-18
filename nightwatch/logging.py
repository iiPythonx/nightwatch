# Copyright (c) 2024 iiPython

# Initialization
class NightwatchLogger():
    def __init__(self) -> None:
        self._color_map = {
            "info": "34", "warn": "33", "error": "31", "critical": "31"
        }

    def log(self, level: str, component: str, message: str) -> None:
        print(f"\033[{self._color_map[level]}m⚡︎ {level.upper()} ({component}): {message}\033[0m")

    # Submethods
    def info(self, *args) -> None:
        self.log("info", *args)

    def warn(self, *args) -> None:
        self.log("warn", *args)

    def error(self, *args) -> None:
        self.log("error", *args)

    def critical(self, *args) -> None:
        self.log("critical", *args)
        exit(1)

log = NightwatchLogger()
