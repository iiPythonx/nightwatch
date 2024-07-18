# Copyright (c) 2024 iiPython

# Modules
from typing import Annotated
from pydantic import BaseModel, StringConstraints
from pydantic_extra_types.color import Color

# Models
class IdentifyModel(BaseModel):
    name: Annotated[str, StringConstraints(min_length = 3, max_length = 32)]
    color: Color
