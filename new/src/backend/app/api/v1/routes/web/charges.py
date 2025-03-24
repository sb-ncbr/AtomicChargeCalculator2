"""Charge calculation routes."""

import asyncio
import uuid

from typing import Annotated, Literal
from fastapi import Depends, File, HTTPException, Path, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.constants import ALLOWED_FILE_TYPES, MAX_SETUP_FILES_SIZE
from api.v1.schemas.response import Response

from core.dependency_injection.container import Container
from core.models.calculation import CalculationSetPreviewDto, ChargeCalculationConfigDto
from core.models.method import Method
from core.models.molecule_info import MoleculeSetStats
from core.models.paging import PagedList
from core.models.parameters import Parameters
from core.models.setup import Setup
from core.models.suitable_methods import SuitableMethods
from core.exceptions.http import BadRequestError, NotFoundError


from db.repositories.calculation_set_repository import CalculationSetFilters
from services.calculation_storage import CalculationStorageService
from services.mmcif import MmCIFService
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
) -> Response[list[Method]]:
    """Returns the list of available methods for charge calculation."""

    try:
        methods = chargefw2.get_available_methods()
        return Response[list[Method]](data=methods)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error getting available methods.",
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
) -> Response[list[Parameters]]:
    """Returns the list of available parameters for the provided method."""

    methods = chargefw2.get_available_methods()
    if not any(method.internal_name == method_name for method in methods):
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Method '{method_name}' not found.",
        )

    try:
        parameters = await chargefw2.get_available_parameters(method_name)
        return Response[list[Parameters]](data=parameters)
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
) -> Response[MoleculeSetStats]:
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
    configs: list[ChargeCalculationConfigDto],
    response_format: Annotated[
        Literal["charges", "none"], Query(description="Output format.")
    ] = "charges",
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
):
    """
    Calculates partial atomic charges for files in the provided directory.
    Returns a list of dictionaries with charges (decimal numbers).
    If no config is provided, the most suitable method and its parameters will be used.
    """

    if configs is None or len(configs) == 0:
        # get most suitable when no config is provided
        configs = [ChargeCalculationConfigDto()]

    if storage_service.get_calculation_set(computation_id) is None:
        raise NotFoundError(detail=f"Computation '{computation_id}' not found.")

    try:
        calculations = await chargefw2.calculate_charges_multi(computation_id, configs)

        if response_format == "none":
            return Response(data=None)

        return Response(data=calculations)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error calculating charges."
        ) from e


@charges_router.post(
    "/setup",
    tags=["setup"],
    description=f"""Stores the provided files on disk and returns the computation id. 
        Allowed file types are {", ".join(ALLOWED_FILE_TYPES)}.""",
)
@inject
async def setup(
    request: Request,
    files: list[UploadFile],
    io: IOService = Depends(Provide[Container.io_service]),
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
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

    user_id = request.state.user.id if request.state.user is not None else None

    try:
        computation_id = str(uuid.uuid4())
        workdir = io.get_input_path(computation_id)
        io.create_dir(workdir)
        await asyncio.gather(*[io.store_upload_file(file, workdir) for file in files])
        storage_service.store_calculation_set(computation_id, user_id, [])

        return Response(data={"computationId": computation_id})
    except Exception as e:
        io.remove_workdir(computation_id)
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error uploading files.",
        ) from e


@charges_router.get("/{computation_id}/mmcif", tags=["mmcif"])
@inject
async def get_mmcif(
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    molecule: Annotated[str | None, Query(description="Molecule name.")] = None,
    io: IOService = Depends(Provide[Container.io_service]),
    mmcif_service: MmCIFService = Depends(Provide[Container.mmcif_service]),
) -> FileResponse:
    """Returns a mmcif file for the provided molecule in the computation."""

    try:
        charges_path = io.get_charges_path(computation_id)
        mmcif_path = mmcif_service.get_molecule_mmcif(charges_path, molecule)
        return FileResponse(path=mmcif_path)
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"MMCIF file for molecule '{molecule}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting MMCIF data.",
        ) from e


@charges_router.get("/examples/{example_id}/mmcif", tags=["examples", "mmcif"])
@inject
async def get_example_mmcif(
    example_id: Annotated[str, Path(description="ID of the example.", example="phenols")],
    molecule: Annotated[str | None, Query(description="Molecule name.")] = None,
    io: IOService = Depends(Provide[Container.io_service]),
    mmcif_service: MmCIFService = Depends(Provide[Container.mmcif_service]),
) -> FileResponse:
    """Returns a mmcif file for the provided molecule in the example."""
    try:
        examples_path = io.get_example_path(example_id)
        mmcif_path = mmcif_service.get_molecule_mmcif(examples_path, molecule)
        return FileResponse(path=mmcif_path)
    except FileNotFoundError as e:
        raise NotFoundError(
            detail=f"MMCIF file for molecule '{molecule}' in example '{example_id}' not found."
        ) from e
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
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[str]]:
    """Returns the list of molecules in the provided computation."""
    try:
        charges_path = io.get_charges_path(computation_id)
        molecules = chargefw2.get_calculation_molecules(charges_path)
        return Response(data=sorted(molecules))
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"Computation '{computation_id}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting molecules.",
        ) from e


@charges_router.get("/examples/{example_id}/molecules", tags=["examples", "molecules"])
@inject
async def get_example_molecules(
    example_id: Annotated[str, Path(description="Id of the example.", example="phenols")],
    io: IOService = Depends(Provide[Container.io_service]),
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[str]]:
    """Returns the list of molecules in the provided computation."""
    try:
        charges_path = io.get_example_path(example_id)
        molecules = chargefw2.get_calculation_molecules(charges_path)
        return Response(data=sorted(molecules))
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"Example '{example_id}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting molecules.",
        ) from e


@charges_router.get("/calculations", tags=["calculations"])
@inject
async def get_calculations(
    request: Request,
    page: Annotated[int, Query(description="Page number.")] = 1,
    page_size: Annotated[int, Query(description="Number of items per page.")] = 10,
    order_by: Annotated[Literal["created_at"], Query(description="Order by field.")] = "created_at",
    order: Annotated[Literal["asc", "desc"], Query(description="Order direction.")] = "desc",
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
) -> Response[PagedList[CalculationSetPreviewDto]]:
    """Returns all calculations stored in the database."""
    user = request.state.user

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be logged in to get calculations.",
        )

    try:
        filters = CalculationSetFilters(
            order=order, order_by=order_by, page=page, page_size=page_size, user_id=user.id
        )
        calculations = storage_service.get_calculations(filters)
        return Response(data=calculations)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting calculations."
        ) from e


@charges_router.get("/{computation_id}/download", tags=["download"])
@inject
async def download_charges(
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    io: IOService = Depends(Provide[Container.io_service]),
) -> FileResponse:
    """Returns a zip file with all charges for the provided computation."""

    try:
        charges_path = io.get_charges_path(computation_id)
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
