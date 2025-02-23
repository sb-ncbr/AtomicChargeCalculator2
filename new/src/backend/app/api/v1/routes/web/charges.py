"""Charge calculation routes."""

import asyncio
import os
from typing import Annotated, Literal
import uuid
from fastapi import Depends, File, Path, Query, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.constants import ALLOWED_FILE_TYPES, CHARGES_OUTPUT_EXTENSION, MAX_SETUP_FILES_SIZE
from api.v1.schemas.response import Response

from core.dependency_injection.container import Container
from core.models.calculation import ChargeCalculationConfig
from core.models.molecule_info import MoleculeInfo
from core.models.setup import Setup
from core.models.suitable_methods import SuitableMethods
from core.exceptions.http import BadRequestError, NotFoundError


from services.io import IOService
from services.chargefw2 import ChargeFW2Service

charges_router = APIRouter(prefix="/charges", tags=["charges"])


@charges_router.get(
    "/methods",
    tags=["methods"],
)
@inject
async def available_methods(
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[str]]:
    """Returns the list of available methods for charge calculation."""

    try:
        methods = await chargefw2.get_available_methods()
        return Response[list[str]](data=methods)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting available methods."
        ) from e


@charges_router.post("/methods", tags=["methods"])
@inject
async def suitable_methods(
    computation_id: str, chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service])
) -> Response[SuitableMethods]:
    """Returns suitable methods for the provided computation."""
    try:
        data = await chargefw2.get_suitable_methods(computation_id)
        return Response(data=data)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting suitable methods."
        ) from e


@charges_router.get("/parameters/{method_name}", tags=["parameters"])
@inject
async def available_parameters(
    method_name: Annotated[
        str,
        Path(
            description="""
            Method name to get parameters for. 
            One of the available methods (list can be received from GET "/api/v1/methods").
            """
        ),
    ],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[str]]:
    """Returns the list of available parameters for the provided method."""

    methods = await chargefw2.get_available_methods()
    if method_name not in methods:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Method '{method_name}' not found.",
        )

    try:
        parameters = await chargefw2.get_available_parameters(method_name)
        return Response[list[str]](data=parameters)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting available parameters for method '{method_name}'.",
        ) from e


@charges_router.post("/info", tags=["info"])
@inject
async def info(
    file: Annotated[UploadFile, File(description="File for which to get information.")],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[MoleculeInfo]:
    """
    Returns information about the provided file.
    Number of molecules, total atoms and individual atoms.
    """

    try:
        info_data = await chargefw2.info(file)
        return Response(data=info_data)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting file information."
        ) from e


@charges_router.post("/{computation_id}/calculate", tags=["calculate"])
@inject
async def calculate_charges(
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    configs: list[ChargeCalculationConfig],
    response_format: Annotated[
        Literal["charges", "none"], Query(description="Output format.")
    ] = "charges",
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
    """
    Calculates partial atomic charges for files in the provided directory.
    Returns a list of dictionaries with charges (decimal numbers).
    """

    if configs is None or len(configs) == 0:
        raise BadRequestError(status_code=status.HTTP_400_BAD_REQUEST, detail="No config provided.")

    try:
        calculations = await asyncio.gather(
            *[chargefw2.calculate_charges(computation_id, config) for config in configs]
        )
        _ = chargefw2.write_to_mmcif(computation_id, calculations)

        if response_format == "none":
            return Response(data=None)

        return Response(data=calculations)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating charges. {str(e)}"
        ) from e


@charges_router.post(
    "/setup",
    tags=["setup"],
    description=f"""Stores the provided files on disk and returns the computation id. 
        Allowed file types are {", ".join(ALLOWED_FILE_TYPES)}.""",
)
@inject
async def setup(
    files: list[UploadFile], io: IOService = Depends(Provide[Container.io_service])
) -> Response[Setup]:
    """Stores the provided files on disk and returns the computation id."""

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

    try:
        computation_id = str(uuid.uuid4())
        tmp_dir = io.create_tmp_dir(io.get_input_path(computation_id))
        await asyncio.gather(*[io.store_upload_file(file, tmp_dir) for file in files])

        return Response(data={"computationId": computation_id})
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error uploading files."
        ) from e


@charges_router.get("/{computation_id}/mmcif", tags=["mmcif"])
@inject
async def get_mmcif(
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    molecule: Annotated[str | None, Query(description="Molecule name.")] = None,
    io: IOService = Depends(Provide[Container.io_service]),
) -> FileResponse:
    """Returns a mmcif file for the provided molecule in the computation."""

    try:
        charges_path = io.get_charges_path(computation_id)
        if not io.path_exists(charges_path):
            raise FileNotFoundError()

        if molecule is None:
            molecules = [file for file in io.listdir(charges_path) if file.endswith(".fw2.cif")]

            if len(molecules) == 0:
                raise FileNotFoundError()

            return FileResponse(path=os.path.join(charges_path, molecules[0]))

        path = os.path.join(io.get_charges_path(computation_id), f"{molecule.lower()}.fw2.cif")
        if not io.path_exists(path):
            raise FileNotFoundError()

        return FileResponse(path=path)
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"MMCIF file for molecule '{molecule}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting MMCIF data.",
        ) from e


@charges_router.get("/{computation_id}/molecules", tags=["molecules"])
@inject
async def get_molecules(
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    io: IOService = Depends(Provide[Container.io_service]),
) -> Response[list[str]]:
    """Returns the list of molecules in the provided computation."""
    try:
        charges_path = io.get_charges_path(computation_id)
        if not io.path_exists(charges_path):
            raise FileNotFoundError()
        molecule_files = [
            file for file in io.listdir(charges_path) if file.endswith(CHARGES_OUTPUT_EXTENSION)
        ]
        molecules = [file.replace(CHARGES_OUTPUT_EXTENSION, "") for file in molecule_files]

        return Response(data=sorted(molecules))
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"Computation '{computation_id}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting molecules.",
        ) from e


# @charges_router.get("/calculations", tags=["calculations"])
# @inject
# async def get_calculations(
#     page: Annotated[int, Query(description="Page number.")] = 1,
#     page_size: Annotated[int, Query(description="Number of items per page.")] = 10,
#     chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
# ):
#     """Returns all calculations stored in the database."""

#     try:
#         filters = PagingFilters(page=page, page_size=page_size)
#         calculations = chargefw2.get_calculations(filters)
#         return calculations  # use Response here
#     except Exception as e:
#         raise BadRequestError(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error getting calculations. {str(e)}"
#         ) from e
