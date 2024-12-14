# Copyright (c) 2024 iiPython

# Modules
import os
import base64
import binascii

from fastapi import Response
from requests import RequestException
from fastapi.responses import JSONResponse

from nightwatch.rics import app, session
from nightwatch.logging import log

# Exceptions
class IllegalURL(Exception):
    pass

# Handle image forwarding
PROXY_SIZE_LIMIT = 10 * (1024 ** 2)

FORWARD_DOMAIN = os.getenv("DOMAIN") 
if FORWARD_DOMAIN is None:
    log.warn("images", "DOMAIN environment variable not set! Image forwarding unprotected!")

# Routing
@app.get("/api/fwd/{public_url:str}", response_model = None)
async def forward_image(public_url: str) -> Response | JSONResponse:
    try:
        new_url = f"https://{base64.b64decode(public_url.replace('_', '/'), validate = True).decode('ascii').rstrip('/')}"
        if FORWARD_DOMAIN and FORWARD_DOMAIN in new_url:
            raise IllegalURL

    except (binascii.Error, UnicodeDecodeError):
        return JSONResponse({"code": 400, "message": "Failed to contact the specified URI."}, status_code = 400)

    except IllegalURL:
        return JSONResponse({"code": 400, "message": "Requested URL contains an illegal string!"}, status_code = 400)

    try:
        data = b""
        with session.get(new_url, stream = True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(PROXY_SIZE_LIMIT):
                data += chunk
                if len(data) >= PROXY_SIZE_LIMIT:
                    return JSONResponse({"code": 400, "message": "Specified URI contains data above size limit."}, status_code = 400)

            return Response(
                data,
                response.status_code,
                {
                    k: v
                    for k, v in response.headers.items() if k in ["Content-Type", "Cache-Control"]
                }
            )

    except RequestException:
        return JSONResponse({"code": 400, "message": "Failed to contact the specified URI."}, status_code = 400)
