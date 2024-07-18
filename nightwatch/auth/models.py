# Copyright (c) 2024 iiPython

# Modules
from typing import Annotated
from pydantic import BaseModel, HttpUrl, SecretStr, StringConstraints

# Models
class BaseAuthenticationModel(BaseModel):
    username: Annotated[str, StringConstraints(min_length = 4, max_length = 36)]
    password: Annotated[SecretStr, StringConstraints(min_length = 8, max_length = 512)]

class AuthorizeModel(BaseModel):
    server: HttpUrl

    # Force token length to 64 characters thanks to 32 byte secret
    token: Annotated[SecretStr, StringConstraints(min_length = 64, max_length = 64)]
