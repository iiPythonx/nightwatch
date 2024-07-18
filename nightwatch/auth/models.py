# Copyright (c) 2024 iiPython

# Modules
from typing import Annotated
from pydantic import BaseModel, HttpUrl, StringConstraints

# Models
class BaseAuthenticationModel(BaseModel):
    username: Annotated[str, StringConstraints(min_length = 4, max_length = 36)]
    password: Annotated[str, StringConstraints(min_length = 8, max_length = 512)]

class LoginModel(BaseAuthenticationModel):
    server: HttpUrl
