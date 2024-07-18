# Copyright (c) 2024 iiPython

# Modules
import secrets

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

        # Connect to database
        self.db = mongo.nightwatch_auth

app: AuthenticationServer = AuthenticationServer()

# Routing
@app.post(path = "/api/profile")
async def route_api_profile(payload: models.BaseTokenModel) -> JSONResponse:
    """Fetches a users profile. This method is POST to prevent query strings with account tokens
    from being logged via uvicorn or whatever HTTP server is running at the moment."""
    response: dict | None = app.db.tokens.find_one(filter = {"token": payload.token.get_secret_value()})
    if response is None:
        return JSONResponse(
            content = {"code": 403, "data": "Invalid account token."},
            status_code = 403
        )

    return JSONResponse(content = {"code": 200, "data": {
        "domain": config["server.domain"],
        "username": response["username"]
    }})

@app.post(path = "/api/authorize")
async def route_api_authorize(payload: models.AuthorizeModel) -> JSONResponse:
    """Authorizes a new external Nightwatch server with a burner account token."""
    response: dict | None = app.db.users.find_one(filter = {"token": payload.token.get_secret_value()})
    if response is None:
        return JSONResponse(
            content = {"comde": 403, "data": "Invalid account token."},
            status_code = 403
        )

    token_filter: dict = {"username": response["username"], "server": payload.server.host}

    # Check for existing token
    existing_token: dict | None = app.db.tokens.find_one(filter = token_filter)
    if existing_token is not None:
        return JSONResponse(content = {"code": 200, "data": existing_token["token"]})

    new_token: str = secrets.token_hex(nbytes = 32)
    app.db.tokens.insert_one(document = token_filter | {"token": new_token})
    return JSONResponse(content = {"code": 200, "data": new_token})

@app.post(path = "/api/signup")
async def route_api_signup(payload: models.BaseAuthenticationModel) -> JSONResponse:
    """Creates a new account and returns its token given a basic username and password."""
    response: dict | None = app.db.users.find_one(filter = {"username": payload.username})
    if response is not None:
        return JSONResponse(
            content = {"code": 400, "data": "An account with that username already exists."},
            status_code = 400
        )

    # Create account
    token: str = secrets.token_hex(nbytes = 32)
    app.db.users.insert_one(document = {
        "username": payload.username,
        "password": app.hasher.hash(password = payload.password.get_secret_value()),
        "token": token
    })
    return JSONResponse(content = {"code": 200, "data": token})

@app.post(path = "/api/login")
async def route_api_login(payload: models.BaseAuthenticationModel) -> JSONResponse:
    """Logs in and returns the master token for a given account."""
    response: dict | None = app.db.users.find_one(filter = {"username": payload.username})
    if response is None:
        return JSONResponse(
            content = {"code": 404, "data": "No account with that username exists."},
            status_code = 404
        )

    try:
        app.hasher.verify(hash = response["password"], password = payload.password.get_secret_value())
        if app.hasher.check_needs_rehash(hash = response["password"]):
            app.db.users.update_one(
                filter = {"username": payload.username},
                update = {"password": app.hasher.hash(password = payload.password.get_secret_value())}
            )

        return JSONResponse(content = {"code": 200, "data": response["token"]})

    except argon2.exceptions.VerificationError:
        log.warn("auth", f"Failed authentication attempt for user '{payload.username}'.")
        return JSONResponse(
            content = {"code": 403, "data": "Invalid password."},
            status_code = 403
        )
