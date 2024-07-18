# Copyright (c) 2024 iiPython

# Modules
from fastapi import FastAPI

import argon2
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from nightwatch.config import config
from nightwatch.logging import log

from . import models

# Initialization
class AuthenticationServer(FastAPI):
    def __init__(self) -> None:
        super().__init__()

        # Initialize Argon2
        self.hasher = argon2.PasswordHasher()

        # Establish MongoDB connection
        mongo: MongoClient = MongoClient(
            host = config["server.connections.mongodb"],
            serverSelectionTimeoutMS = 5000
        )
        mongo.admin.command("ping")

        # Connect to Nightwatch / Authentication to avoid pollution
        self.db = mongo.nightwatch.auth

app: AuthenticationServer = AuthenticationServer()

# Routing
@app.post(path = "/api/login")
async def route_api_login(payload: models.LoginModel) -> JSONResponse:
    response: dict | None = app.db.find_one(filter = {"username": payload.username})
    if response is None:
        return JSONResponse(
            content = {"code": 400, "data": "No account with that username exists."},
            status_code = 400
        )

    # Check password
    

    return JSONResponse(content = {"code": 200, "data": "Logging in isn't a thing yet bud."})
