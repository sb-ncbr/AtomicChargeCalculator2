"""Charge calculation routes."""

from typing import Annotated
from fastapi import Depends, File, Path, Query, UploadFile, status
from fastapi.routing import APIRouter
from dependency_injector.wiring import inject, Provide

from api.v1.schemas.response import Response

from core.dependency_injection.container import Container
from core.models.calculation import ChargeCalculationConfig
from core.models.paging import PagingFilters
from core.exceptions.http import BadRequestError


from services.chargefw2 import ChargeFW2Service

charges_router = APIRouter(prefix="/charges", tags=["charges"])


@charges_router.get(
    "/methods",
    tags=["methods"],
)
@inject
async def available_methods(
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
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
    file: UploadFile, chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service])
):
    """Returns the list of suitable methods for the provided file.

    **file**: File to get suitable methods for.
    """

    try:
        methods = await chargefw2.get_suitable_methods(file)
        return Response[list[dict]](data=methods)
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
):
    """Returns the list of available parameters for the provided method."""

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
):
    """
    Returns information about the provided file.
    Number of molecules, total atoms and individual atoms.
    """

    try:
        info_data = await chargefw2.info(file)
        return Response(data=info_data)
    except Exception as e:
        raise BadRequestError(
            status_status_code=status.HTTP_400_BAD_REQUEST, detail="Error getting file information."
        ) from e


@charges_router.post(
    "/calculate",
    tags=["calculate"],
    openapi_extra={"x-allowed-file-types": ["sdf", "mol2", "pdb", "mmcif"]},  # example
)
@inject
async def calculate_charges(
    files: list[UploadFile],
    method_name: Annotated[str, Query(description="Method name to calculate charges with.")],
    parameters_name: Annotated[
        str | None, Query(description="Parameters name to be used with the provided method.")
    ] = None,
    read_hetatm: Annotated[
        bool, Query(description="Read HETATM records from PDB/mmCIF files.")
    ] = True,
    ignore_water: Annotated[
        bool, Query(description="Discard water molecules from PDB/mmCIF files.")
    ] = False,
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
    """
    Calculates partial atomic charges for the provided files.
    Returns a list of dictionaries with charges (decimal numbers).
    """

    try:
        config = ChargeCalculationConfig(
            method=method_name,
            parameters=parameters_name,
            read_hetatm=read_hetatm,
            ignore_water=ignore_water,
        )
        calculations = await chargefw2.calculate_charges(files, config)
        return Response(
            data=calculations, total_count=len(calculations), page_size=len(calculations)
        )
    except Exception as e:
        raise BadRequestError(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating charges. {str(e)}"
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
