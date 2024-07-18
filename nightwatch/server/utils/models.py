# Copyright (c) 2024 iiPython

# Modules
from typing import Annotated
from pydantic import BaseModel, PlainSerializer, StringConstraints
from pydantic_extra_types.color import Color

# Models
class IdentifyModel(BaseModel):
    name: Annotated[str, StringConstraints(min_length = 3, max_length = 32)]
    color: Annotated[Color, PlainSerializer(lambda c: c.as_hex(), return_type = str, when_used = "always")]

class MessageModel(BaseModel):
    text: Annotated[str, StringConstraints(min_length = 1, max_length = 300)]
