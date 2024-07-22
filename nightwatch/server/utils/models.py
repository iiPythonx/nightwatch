# Copyright (c) 2024 iiPython

# Modules
from typing import Annotated
from pydantic import BaseModel, HttpUrl, SecretStr, StringConstraints

# Models
class MessageModel(BaseModel):
    text: Annotated[str, StringConstraints(min_length = 1, max_length = 300)]

class IdentifyModel(BaseModel):
    auth_server: HttpUrl

    # Force token length to 64 characters thanks to 32 byte secret
    token: Annotated[SecretStr, StringConstraints(min_length = 64, max_length = 64)]
