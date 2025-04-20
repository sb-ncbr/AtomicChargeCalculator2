"""File manipulation routes."""

import asyncio
import traceback

import pathlib

from typing import Annotated, Literal
from fastapi import Depends, Path, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.constants import ALLOWED_FILE_TYPES
from api.v1.schemas.response import Response
from api.v1.schemas.file import QuotaResponse, UploadResponse, FileResponse as FileResponseModel
from api.v1.exceptions import BadRequestError, NotFoundError

from models.paging import PagedList

from api.v1.container import Container


from services.file_storage import FileStorageService
from services.chargefw2 import ChargeFW2Service
from services.calculation_storage import CalculationStorageService
from services.io import IOService

files_router = APIRouter(prefix="/files", tags=["files"])


@files_router.get(path="")
@inject
async def get_files(
    request: Request,
    page: Annotated[int, Query(description="Page number", ge=1)] = 1,
    page_size: Annotated[int, Query(description="Number of items per page", ge=1)] = 10,
    order_by: Annotated[
        Literal["name", "uploaded_at", "size"], Query(description="Order by")
    ] = "uploaded_at",
    search: Annotated[str, Query(description="Search term")] = "",
    order: Annotated[Literal["asc", "desc"], Query(description="Order direction.")] = "desc",
    storage_service: FileStorageService = Depends(Provide[Container.file_storage_service]),
) -> Response[PagedList[FileResponseModel]]:
    """Returns the list of files uploaded by the user.."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    if user_id is None:
        raise BadRequestError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to be logged in to get files.",
        )

    try:
        data = storage_service.get_files(
            order_by=order_by,
            order=order,
            page=page,
            page_size=page_size,
            search=search,
            user_id=user_id,
        )

        return Response(data=data)
    except Exception as e:
        traceback.print_exc()
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error getting files.",
        ) from e


@files_router.post(
    "/upload",
    description="Stores the provided files on disk and returns their ids. "
    + f"Allowed file types are {', '.join(ALLOWED_FILE_TYPES)}.",
)
@inject
async def upload(
    request: Request,
    files: list[UploadFile],
    io: IOService = Depends(Provide[Container.io_service]),
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[UploadResponse]]:
    """Stores the provided files on disk and returns the computation id."""

    def is_ext_valid(filename: str) -> bool:
        parts = filename.rsplit(".", 1)
        ext = parts[-1]

        # has extension and is extension allowed
        return len(parts) == 2 and ext in ALLOWED_FILE_TYPES

    if len(files) == 0:
        raise BadRequestError(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided.")

    if any(file.size > io.max_file_size for file in files):
        max_file_size_mb = io.max_file_size / 1024 / 1024
        raise BadRequestError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Unable to upload files. One or more files are too large. "
            + f"Maximum allowed size is {max_file_size_mb} MB.",
        )

    user_id = str(request.state.user.id) if request.state.user is not None else None

    if user_id is not None:
        _, available_b, quota_b = io.get_quota(user_id)
        upload_size_b = sum(file.size for file in files)
        if upload_size_b > available_b:
            quota_mb = quota_b / 1024 / 1024
            raise BadRequestError(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to upload files. Quota exceeded. "
                + f"Maximum storage space is {quota_mb} MB.",
            )
    else:
        _, available, _ = io.get_quota()
        upload_size_b = sum(file.size for file in files)
        if upload_size_b > available:
            io.free_guest_file_space(upload_size_b)

    if not all(is_ext_valid(file.filename) for file in files):
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed file types are {', '.join(ALLOWED_FILE_TYPES)}",
        )

    try:
        workdir = io.get_file_storage_path(user_id)
        io.create_dir(workdir)

        stored_files = await asyncio.gather(
            *[io.store_upload_file(file, workdir) for file in files]
        )

        for [path, file_hash] in stored_files:
            info = await chargefw2.info(path)
            storage_service.store_file_info(file_hash, info)

        data = [
            UploadResponse(file=io.parse_filename(pathlib.Path(name).name)[1], file_hash=file_hash)
            for [name, file_hash] in stored_files
        ]

        return Response(data=data)
    except Exception as e:
        traceback.print_exc()
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error uploading files.",
        ) from e


@files_router.get("/download/computation/{computation_id}")
@inject
async def download_charges(
    request: Request,
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    io: IOService = Depends(Provide[Container.io_service]),
) -> FileResponse:
    """Returns a zip file with all charges for the provided computation."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    try:
        charges_path = io.get_charges_path(computation_id, user_id)
        if not io.path_exists(charges_path):
            raise FileNotFoundError()

        archive_path = io.zip_charges(charges_path)

        return FileResponse(path=archive_path, media_type="application/zip")
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"Computation '{computation_id}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error downloading charges."
        ) from e


@files_router.get("/quota")
@inject
async def get_quota(
    request: Request,
    io: IOService = Depends(Provide[Container.io_service]),
) -> Response[QuotaResponse]:
    """Returns the quota of the user."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    if user_id is None:
        raise BadRequestError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to be logged in to see quota.",
        )

    try:
        used, available, quota = io.get_quota(user_id)
        return Response(data=QuotaResponse(used_space=used, available_space=available, quota=quota))
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error getting files.",
        ) from e


@files_router.delete("/{file_hash}")
@inject
async def delete_file(
    request: Request,
    file_hash: Annotated[str, Path(description="UUID of the file to delete.")],
    io: IOService = Depends(Provide[Container.io_service]),
) -> Response[None]:
    """Deletes all files uploaded by the user."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    if user_id is None:
        raise BadRequestError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to be logged in to delete files.",
        )

    try:
        io.remove_file(file_hash, user_id)
        return Response(data=None)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error deleting files.",
        ) from e


@files_router.get("/download/file/{file_hash}")
@inject
async def download_file(
    request: Request,
    file_hash: Annotated[str, Path(description="Hash of the file to download.")],
    io: IOService = Depends(Provide[Container.io_service]),
) -> FileResponse:
    """Returns a zip file with all charges for the provided computation."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    try:
        file_path = io.get_filepath(file_hash, user_id)
        if not io.path_exists(file_path):
            raise FileNotFoundError()

        return FileResponse(path=file_path, media_type="application/octet-stream")
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"File '{file_hash}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error downloading file."
        ) from e
