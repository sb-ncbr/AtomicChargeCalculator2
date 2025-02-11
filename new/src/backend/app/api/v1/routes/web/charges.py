"""Charge calculation routes."""

import asyncio
from typing import Annotated
import uuid
from fastapi import Depends, File, Path, Query, UploadFile, status
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.constants import ALLOWED_FILE_TYPES, MAX_SETUP_FILES_SIZE
from api.v1.schemas.response import Response

from core.dependency_injection.container import Container
from core.models.calculation import ChargeCalculationConfig, ChargeCalculationResult
from core.models.molecule_info import MoleculeInfo
from core.models.paging import PagingFilters
from core.models.setup import Setup
from core.models.suitable_methods import SuitableMethods
from core.exceptions.http import BadRequestError


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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting available parameters."
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


# @charges_router.post("/calculate/old", tags=["calculate"])
# @inject
# async def calculate_charges(
#     files: list[UploadFile],
#     method_name: Annotated[str, Query(description="Method name to calculate charges with.")],
#     parameters_name: Annotated[
#         str | None, Query(description="Parameters name to be used with the provided method.")
#     ] = None,
#     read_hetatm: Annotated[
#         bool, Query(description="Read HETATM records from PDB/mmCIF files.")
#     ] = True,
#     ignore_water: Annotated[
#         bool, Query(description="Discard water molecules from PDB/mmCIF files.")
#     ] = False,
#     chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
# ):
#     """
#     Calculates partial atomic charges for the provided files.
#     Returns a list of dictionaries with charges (decimal numbers).
#     """

#     try:
#         config = ChargeCalculationConfig(
#             method=method_name,
#             parameters=parameters_name,
#             read_hetatm=read_hetatm,
#             ignore_water=ignore_water,
#         )
#         calculations = await chargefw2.calculate_charges(files, config)
#         return Response(
#             data=calculations, total_count=len(calculations), page_size=len(calculations)
#         )
#     except Exception as e:
#         raise BadRequestError(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating charges. {str(e)}"
#         ) from e


@charges_router.post("/calculate", tags=["calculate"])
@inject
async def calculate_charges(
    computation_id: Annotated[str, Query(description="UUID of the computation.")],
    configs: list[ChargeCalculationConfig],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[ChargeCalculationResult]]:
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

    # TODO: move closure somewhere else
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
        tmp_dir = io.create_tmp_dir(computation_id)
        await asyncio.gather(*[io.store_upload_file(file, tmp_dir) for file in files])

        return Response(data={"computationId": computation_id})
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error uploading files. {str(e)}"
        ) from e


@charges_router.get("/calculations", tags=["calculations"])
@inject
async def get_calculations(
    page: Annotated[int, Query(description="Page number.")] = 1,
    page_size: Annotated[int, Query(description="Number of items per page.")] = 10,
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
    """Returns all calculations stored in the database."""

    try:
        filters = PagingFilters(page=page, page_size=page_size)
        calculations = chargefw2.get_calculations(filters)
        return calculations  # use Response here
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error getting calculations. {str(e)}"
        ) from e
