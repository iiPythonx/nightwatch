# Copyright (c) 2024 iiPython

# Modules
import secrets

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

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
        self.add_middleware(
            CORSMiddleware,
            allow_origins = "*",
            allow_credentials = True,
            allow_methods = ["POST"],
            allow_headers = ["*"]
        )

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

# Handle errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error, message = exc.errors()[0], str(exc)  # Just focus on one
    match error["type"]:
        case "too_short" | "string_too_short":
            message = f"{error['loc'][1].capitalize()} should be at least {error['ctx']['min_length']} characters."

        case "too_long" | "string_too_long":
            message = f"{error['loc'][1].capitalize()} should be {error['ctx']['max_length']} characters at most."

        case "missing":
            message = f"{error['loc'][1].capitalize()} needs to be specified."

        case "string_type":
            message = f"{error['loc'][1].capitalize()} must be a valid string."

        case "url_type" | "url_scheme" | "url_parsing":
            message = f"{error['loc'][1].capitalize()} must be a valid URL."

    return JSONResponse(
        status_code = 422,
        content = {"code": 422, "data": message}
    )

# Routing
@app.post(path = "/api/profile")
async def route_api_profile(payload: models.BaseTokenModel) -> JSONResponse:
    """Fetches a users profile. This method is POST to prevent query strings with account tokens
    from being logged via uvicorn or whatever HTTP server is running at the moment."""
    response: dict | None = app.db.tokens.find_one(filter = {"token": payload.token.get_secret_value()}) or \
        app.db.users.find_one(filter = {"token": payload.token.get_secret_value()})

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
            content = {"code": 403, "data": "Invalid account token."},
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
