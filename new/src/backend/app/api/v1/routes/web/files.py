"""File manipulation routes."""

import asyncio
import traceback

import pathlib

from typing import Annotated, Any
from fastapi import Depends, Path, Request, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.constants import ALLOWED_FILE_TYPES, MAX_SETUP_FILES_SIZE
from api.v1.schemas.response import Response

from core.dependency_injection.container import Container
from core.exceptions.http import BadRequestError, NotFoundError


from db.models.moleculeset_stats import AtomTypeCount, MoleculeSetStats
from services.chargefw2 import ChargeFW2Service
from services.calculation_storage import CalculationStorageService
from services.io import IOService

files_router = APIRouter(prefix="/files", tags=["files"])


@files_router.get(path="")
@inject
async def get_files(
    request: Request, io: IOService = Depends(Provide[Container.io_service])
) -> Response:
    """Returns the list of files uploaded by the user.."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    if user_id is None:
        raise BadRequestError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to be logged in to get files.",
        )

    try:
        workdir = io.get_file_storage_path(user_id)
        files = [io.parse_filename(pathlib.Path(name).name) for name in io.listdir(workdir)]

        data = [{"file": name, "file_hash": file_hash} for [file_hash, name] in files]
        return Response(data=data)
    except Exception as e:
        traceback.print_exc()
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error getting files.",
        ) from e


@files_router.post(
    "/upload",
    description=f"""Stores the provided files on disk and returns their ids. 
        Allowed file types are {", ".join(ALLOWED_FILE_TYPES)}.""",
)
@inject
async def upload(
    request: Request,
    files: list[UploadFile],
    io: IOService = Depends(Provide[Container.io_service]),
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[Any]:
    """Stores the provided files on disk and returns the computation id."""

    # TODO: add quota check

    def is_ext_valid(filename: str) -> bool:
        parts = filename.rsplit(".", 1)
        ext = parts[-1]

        # has extension and is extension allowed
        return len(parts) == 2 and ext in ALLOWED_FILE_TYPES

    if len(files) == 0:
        raise BadRequestError(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided.")

    if sum(file.size for file in files) > MAX_SETUP_FILES_SIZE:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum upload size is 250MB."
        )

    if not all(is_ext_valid(file.filename) for file in files):
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed file types are {', '.join(ALLOWED_FILE_TYPES)}",
        )

    user_id = str(request.state.user.id) if request.state.user is not None else None
    try:
        workdir = io.get_file_storage_path(user_id)
        io.create_dir(workdir)

        files = await asyncio.gather(*[io.store_upload_file(file, workdir) for file in files])

        for [path, file_hash] in files:
            info = await chargefw2.info(path)
            storage_service.store_file_info(
                MoleculeSetStats(
                    file_hash=file_hash,
                    total_molecules=info.total_molecules,
                    total_atoms=info.total_atoms,
                    atom_type_counts=[
                        AtomTypeCount(symbol=count.symbol, count=count.count)
                        for count in info.atom_type_counts
                    ],
                ),
            )

        data = [
            {"file": io.parse_filename(pathlib.Path(name).name)[1], "file_hash": file_hash}
            for [name, file_hash] in files
        ]

        return Response(data=data)
    except Exception as e:
        traceback.print_exc()
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error uploading files.",
        ) from e


@files_router.get("/{computation_id}/download")
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
