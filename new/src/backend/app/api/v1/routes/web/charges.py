"""Charge calculation routes."""

import uuid


from typing import Annotated, Literal
from fastapi import Depends, File, HTTPException, Path, Query, Request, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.schemas.response import Response

from core.dependency_injection.container import Container
from core.models.calculation import (
    CalculationConfigDto,
    CalculationSetPreviewDto,
)
from core.models.method import Method
from core.models.molecule_info import MoleculeSetStats
from core.models.paging import PagedList
from core.models.parameters import Parameters
from core.models.suitable_methods import SuitableMethods
from core.exceptions.http import BadRequestError, NotFoundError


from db.repositories.calculation_set_repository import CalculationSetFilters
from services.calculation_storage import CalculationStorageService
from services.mmcif import MmCIFService
from services.io import IOService
from services.chargefw2 import ChargeFW2Service

charges_router = APIRouter(prefix="/charges", tags=["charges"])


@charges_router.get("/methods")
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


@charges_router.post("/methods")
@inject
async def suitable_methods(
    request: Request,
    file_hashes: list[str],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[SuitableMethods]:
    """Returns suitable methods for the provided computation."""
    user_id = str(request.state.user.id) if request.state.user is not None else None

    try:
        data = await chargefw2.get_suitable_methods(file_hashes, user_id)
        return Response(data=data)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting suitable methods."
        ) from e


@charges_router.post("/{computation_id}/methods")
@inject
async def computation_suitable_methods(
    request: Request,
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[SuitableMethods]:
    """Returns suitable methods for the provided computation."""
    user_id = str(request.state.user.id) if request.state.user is not None else None

    try:
        data = await chargefw2.get_computation_suitable_methods(
            computation_id,
            user_id,
        )
        return Response(data=data)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting suitable methods."
        ) from e


@charges_router.get("/parameters/{method_name}")
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


@charges_router.post("/info")
@inject
async def info(
    request: Request,
    file_hash: Annotated[str, File(description="Hash of a file for which to get information.")],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
    io_service: IOService = Depends(Provide[Container.io_service]),
) -> Response[MoleculeSetStats]:
    """
    Returns information about the provided file.
    Number of molecules, total atoms and individual atoms.
    """

    user_id = str(request.state.user.id) if request.state.user is not None else None

    try:
        filepath = io_service.get_filepath(file_hash, user_id)

        if filepath is None:
            raise FileNotFoundError()

        info_data = await chargefw2.info(filepath)

        return Response(data=info_data)
    except FileNotFoundError as e:
        raise NotFoundError(detail="File not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting file information."
        ) from e


@charges_router.post("/calculate")
@inject
async def calculate_charges(
    request: Request,
    configs: list[CalculationConfigDto],
    file_hashes: list[str],
    computation_id: str | None = None,
    response_format: Annotated[
        Literal["charges", "none"], Query(description="Output format.")
    ] = "charges",
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
    mmcif_service: MmCIFService = Depends(Provide[Container.mmcif_service]),
    io_service: IOService = Depends(Provide[Container.io_service]),
):
    """
    Calculates partial atomic charges for files in the provided directory.
    Returns a list of dictionaries with charges (decimal numbers).
    If no config is provided, the most suitable method and its parameters will be used.
    """

    user_id = str(request.state.user.id) if request.state.user is not None else None

    if configs is None or len(configs) == 0:
        # get most suitable when no config is provided
        # TODO: calling this endpoint multiple times without config inserts the most suitable one into database
        #  and cache (db) is not being used
        configs = [CalculationConfigDto()]

    computation_id = computation_id or str(uuid.uuid4())

    if (
        file_hashes is None
        or len(file_hashes) == 0
        and storage_service.get_calculation_set(computation_id) is None
    ):
        # if no file hashes provided and computation has not been set up
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file hashes provided.",
        )

    try:
        io_service.prepare_inputs(user_id, computation_id, file_hashes)

        if file_hashes is None or len(file_hashes) == 0:
            # get all files if none provided and computation has already been set up
            inputs_path = io_service.get_inputs_path(computation_id, user_id)
            file_hashes = [
                io_service.parse_filename(file)[0] for file in io_service.listdir(inputs_path)
            ]

        if user_id is not None:
            filtered = storage_service.filter_existing_calculations(
                computation_id, file_hashes, configs
            )
        else:
            # calculate all if not logged in
            filtered = {config: list(file_hashes) for config in configs}

        calculations = await chargefw2.calculate_charges_multi(computation_id, filtered, user_id)

        if user_id is not None:
            storage_service.store_calculation_results(computation_id, calculations, user_id)
            calculations = storage_service.get_calculation_results(computation_id)

        _ = mmcif_service.write_to_mmcif(user_id, computation_id, calculations)

        if response_format == "none":
            return Response(data=computation_id)

        return Response(data=calculations)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error calculating charges."
        ) from e


@charges_router.post("/setup")
@inject
async def setup(
    request: Request,
    file_hashes: list[str],
    io_service: IOService = Depends(Provide[Container.io_service]),
    storage_service: CalculationStorageService = Depends(Provide[Container.storage_service]),
):
    """Prepares input for computation so it can be run later."""

    user_id = str(request.state.user.id) if request.state.user is not None else None
    computation_id = str(uuid.uuid4())

    try:
        io_service.prepare_inputs(user_id, computation_id, file_hashes)
        storage_service.store_calculation_results(computation_id, [], user_id)
        return Response(data=computation_id)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error setting up calculation.."
        ) from e


# chemical/x-cif
@charges_router.get("/{computation_id}/mmcif")
@inject
async def get_mmcif(
    request: Request,
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    molecule: Annotated[str | None, Query(description="Molecule name.")] = None,
    io: IOService = Depends(Provide[Container.io_service]),
    mmcif_service: MmCIFService = Depends(Provide[Container.mmcif_service]),
    set_repository: CalculationStorageService = Depends(Provide[Container.storage_service]),
) -> FileResponse:
    """Returns a mmcif file for the provided molecule in the computation."""

    user_id = str(request.state.user.id) if request.state.user is not None else None

    # this is a workaround because molstar is not able to send cookies when fetching mmcif
    set_exists = set_repository.get_calculation_set(computation_id)
    if set_exists is not None and set_exists.user_id is not None:
        user_id = str(set_exists.user_id)

    try:
        charges_path = io.get_charges_path(computation_id, user_id)
        mmcif_path = mmcif_service.get_molecule_mmcif(charges_path, molecule)
        return FileResponse(path=mmcif_path)
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"MMCIF file for molecule '{molecule}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting MMCIF data.",
        ) from e


@charges_router.get("/examples/{example_id}/mmcif")
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


@charges_router.get("/{computation_id}/molecules")
@inject
async def get_molecules(
    request: Request,
    computation_id: Annotated[str, Path(description="UUID of the computation.")],
    io: IOService = Depends(Provide[Container.io_service]),
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
) -> Response[list[str]]:
    """Returns the list of molecules in the provided computation."""
    user_id = str(request.state.user.id) if request.state.user is not None else None

    try:
        charges_path = io.get_charges_path(computation_id, user_id)
        molecules = chargefw2.get_calculation_molecules(charges_path)
        return Response(data=sorted(molecules))
    except FileNotFoundError as e:
        raise NotFoundError(detail=f"Computation '{computation_id}' not found.") from e
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while getting molecules.",
        ) from e


@charges_router.get("/examples/{example_id}/molecules")
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


@charges_router.get("/calculations")
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
    user_id = str(request.state.user.id) if request.state.user is not None else None

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be logged in to get calculations.",
        )

    try:
        filters = CalculationSetFilters(
            order=order, order_by=order_by, page=page, page_size=page_size, user_id=user_id
        )
        calculations = storage_service.get_calculations(filters)
        return Response(data=calculations)
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting calculations."
        ) from e
