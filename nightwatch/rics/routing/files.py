# Copyright (c) 2024 iiPython

# Modules
import typing
import shutil
import mimetypes
from pathlib import Path

from nanoid import generate
from fastapi import UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, field_validator

from nightwatch.rics import app, config

# Initialization
SIZE_LIMIT = 400 * (1024 ** 2)  # 100MB
CHUNK_LIMIT = SIZE_LIMIT / 4

UPLOAD_LOCATION = Path(config["file_upload_location"] or (config.config_path.parent / "file_uploads"))
UPLOAD_LOCATION.mkdir(parents = True, exist_ok = True)

app.state.uploads = {}

# Models
class FileCreationModel(BaseModel):
    size: typing.Annotated[int, Field(ge = 1, le = SIZE_LIMIT)]  # 1B - SIZE_LIMIT
    name: str

    # Ensure that our filename conforms to ext4 storage requirements
    @field_validator("name")
    def validate_filename(cls, value: str) -> str:
        if "/" in value or "\0" in value:
            raise ValueError("Filename contains / or a null character!")

        if len(value.encode("utf-8")) > 255:
            raise ValueError("Filename must be <= 255 bytes in length!")

        return value

# Handle routing
@app.post("/api/file")
async def route_file_create(file: FileCreationModel) -> JSONResponse:
    file_id = generate()

    # Save this upload
    app.state.uploads[file_id] = file.model_dump()
    return JSONResponse({
        "code": 200,
        "data": {
            "file_id": file_id
        }
    })

@app.post("/api/file/{file_id:str}")
async def route_file_upload(upload: UploadFile, file_id: str) -> JSONResponse:
    if file_id not in app.state.uploads:
        return JSONResponse({"code": 403}, status_code = 403)

    target = app.state.uploads[file_id]
    destination = UPLOAD_LOCATION / file_id / target["name"]

    if not destination.parent.is_dir():
        destination.parent.mkdir()

    existing_size = target.get("written_bytes", 0)
    if existing_size > target["size"]:
        shutil.rmtree(destination.parent)
        del app.state.uploads[file_id]
        return JSONResponse({"code": 400, "message": "File exceeds size limit."}, status_code = 400)

    # Check filesize of this chunk
    upload.file.seek(0, 2)  # Go to end of file
    chunk_size = upload.file.tell()

    if chunk_size > CHUNK_LIMIT:
        if destination.is_file():
            shutil.rmtree(destination.parent)

        del app.state.uploads[file_id]
        return JSONResponse({"code": 400, "message": "Chunk exceeds size limit."}, status_code = 400)

    if existing_size + chunk_size > target["size"]:
        if destination.is_file():
            shutil.rmtree(destination.parent)

        del app.state.uploads[file_id]
        return JSONResponse({"code": 400, "message": "File exceeds size limit."}, status_code = 400)

    # Save to disk
    app.state.uploads[file_id]["written_bytes"] = existing_size + chunk_size
    with destination.open("ab") as handle:
        upload.file.seek(0)
        handle.write(await upload.read())

    return JSONResponse({"code": 200, "data": {"current_size": target["written_bytes"]}})

@app.post("/api/file/{file_id:str}/finalize")
async def route_file_finalize(file_id: str) -> JSONResponse:
    if file_id not in app.state.uploads:
        return JSONResponse({"code": 403}, status_code = 403)

    target = app.state.uploads[file_id]
    if target.get("written_bytes", 0) < 1:
        if (UPLOAD_LOCATION / file_id).is_dir():
            shutil.rmtree(UPLOAD_LOCATION / file_id)

        del app.state.uploads[file_id]
        return JSONResponse({"code": 400, "message": "No data has been written to file."}, status_code = 400)

    del app.state.uploads[file_id]
    return JSONResponse({"code": 200, "data": {"path": f"{file_id}/{target['name']}"}})

@app.get("/api/file/{file_id:str}/info")
async def route_file_info(file_id: str) -> JSONResponse:
    file_path = UPLOAD_LOCATION / file_id
    if not (file_path.is_dir() and file_path.relative_to(UPLOAD_LOCATION)):
        return JSONResponse({"code": 404}, status_code = 404)

    actual_file = next(file_path.iterdir())
    return JSONResponse({
        "code": 200,
        "data": {
            "size": actual_file.stat().st_size,
            "name": actual_file.name
        }
    })

@app.get("/file/{file_id:str}/{file_name:str}", response_model = None)
async def route_file_download(file_id: str, file_name: str) -> FileResponse | JSONResponse:
    file_path = UPLOAD_LOCATION / file_id / file_name
    if not (file_path.is_file() and file_path.relative_to(UPLOAD_LOCATION)):
        return JSONResponse({"code": 404}, status_code = 404)

    content_type = mimetypes.guess_type(file_path.name)[0]
    return FileResponse(
        file_path,
        headers = {
            "Content-Type": content_type or "application/octet-stream",
            "Content-Disposition": "inline" if content_type else "attachment"
        }
    )
