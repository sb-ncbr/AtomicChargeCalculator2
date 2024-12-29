from typing import Annotated
from fastapi import Depends, File, Path, Query, UploadFile
from fastapi.routing import APIRouter
from core.integrations.chargefw2.base import ChargeFW2Base
from core.dependency_injection.container import Container
from dependency_injector.wiring import inject, Provide
from api.v1.schemas.response import ResponseMultiple, ResponseSingle
from services.chargefw2 import ChargeFW2Service

charges_router = APIRouter(prefix="/charges", tags=["charges"])


@charges_router.get(
    "/methods",
    tags=["methods"],
)
@inject
async def available_methods(chargefw2: ChargeFW2Base = Depends(Provide[Container.chargefw2])):
    """
    Returns the list of available methods for charge calculation.
    """

    methods: list[str] = chargefw2.get_available_methods()
    return ResponseMultiple(data=methods, total_count=len(methods), page_size=len(methods))


@charges_router.post("/methods", tags=["methods"])
@inject
async def suitable_methods(
    file: UploadFile, chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service])
):
    """Returns the list of suitable methods for the provided file.

    **file**: File to get suitable methods for.
    """

    methods: list[str] = await chargefw2.get_suitable_methods(file)
    return ResponseMultiple(data=methods, total_count=len(methods), page_size=len(methods))


@charges_router.get("/parameters/{method_name}", tags=["parameters"])
@inject
async def available_parameters(
    method_name: Annotated[
        str,
        Path(
            description='Method name to get parameters for. One of the available methods (list can be received from GET "/api/v1/methods").'
        ),
    ],
    chargefw2: ChargeFW2Base = Depends(Provide[Container.chargefw2]),
):
    """Returns the list of available parameters for the provided method."""

    parameters: list[str] = chargefw2.get_available_parameters(method_name)
    return ResponseMultiple(data=parameters, total_count=len(parameters), page_size=len(parameters))


@charges_router.post("/info", tags=["info"])
@inject
async def info(
    file: Annotated[UploadFile, File(description="File for which to get information.")],
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
    """Returns information about the provided file. Number of molecules, total atoms and individual atoms."""

    info = await chargefw2.info(file)
    return ResponseSingle(data=info)


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
    read_hetatm: Annotated[bool, Query(description="Read HETATM records from PDB/mmCIF files.")] = True,
    ignore_water: Annotated[bool, Query(description="Discard water molecules from PDB/mmCIF files.")] = False,
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
    """Calculates partial atomic charges for the provided files. Returns a list of dictionaries with charges (decimal numbers)."""

    charges = await chargefw2.calculate_charges(files, method_name, parameters_name, read_hetatm, ignore_water)
    return ResponseMultiple(data=charges, total_count=len(charges), page_size=len(charges))
