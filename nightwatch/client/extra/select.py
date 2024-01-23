# Copyright (c) 2024 iiPython

# Modules
import sys
from typing import List

from ..vendor.iipython import color, readchar, keys

# Main menu class
class MenuHandler(object):
    def __init__(self) -> None:
        self._config = {
            "colors": {
                "index": "[blue]{}[/]",
                "highlight": "[yellow]{}[/]"
            },
            "suffix": "[dim]<--[/][norm]",
            "indents": {
                "index": "  ",
                "option": "\t"  # \t = 4 spaces
            },
            "enable_index": True
        }

    def config(self, config: dict) -> None:
        for k, v in config.items():
            self._config[k] = v

    def show(self, options: List[str]) -> str:
        iterated, length, index = 0, len(options), 0
        while True:
            sys.stdout.write(f"\033[{length}F" * iterated)

            # Handle control
            if iterated:
                key = readchar()
                if key in [keys.UP, "w"]:
                    index = length - 1 if index - 1 < 0 else index - 1

                elif key in [keys.DOWN, "s"]:
                    index = 0 if index + 1 >= length else index + 1

                elif key == keys.ENTER:
                    sys.stdout.write("\n" * length)
                    sys.stdout.flush()
                    return options[index]

                elif key == keys.CTRL_C:
                    raise KeyboardInterrupt

            # Print out options
            _i = self._config["indents"]
            for i, option in enumerate(options):
                index_text = color(self._config["colors"]["index"].format(i + 1))
                if i == index:
                    option_text = color(self._config["colors"]["highlight"].format(option))
                    suffix_text = color(self._config["suffix"]) if self._config["suffix"] else ""

                else:
                    option_text, suffix_text = option, ""

                index_text = f"{_i['index']}{index_text}" if self._config["enable_index"] else ""
                sys.stdout.write(f"\033[2K{index_text}{_i['option']}{option_text} {suffix_text}\n")

            iterated = 1

menu = MenuHandler()
