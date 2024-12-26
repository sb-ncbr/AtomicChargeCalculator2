from fastapi import Depends, UploadFile
from fastapi.routing import APIRouter
from core.integrations.chargefw2.base import ChargeFW2Base
from core.dependency_injection.container import Container
from dependency_injector.wiring import inject, Provide
from api.v1.schemas.response import ResponseMultiple, ResponseSingle
from services.chargefw2 import ChargeFW2Service

charges_router = APIRouter(prefix="/charges", tags=["charges"])


@charges_router.get("/methods", tags=["charges", "methods"])
@inject
async def available_methods(chargefw2: ChargeFW2Base = Depends(Provide[Container.chargefw2])):
    methods: list[str] = chargefw2.get_available_methods()
    return ResponseMultiple(data=methods, total_count=len(methods), page_size=len(methods))


@charges_router.post("/methods", tags=["charges", "methods"])
@inject
async def suitable_methods(
    file: UploadFile, chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service])
):
    methods: list[str] = await chargefw2.get_suitable_methods(file)
    return ResponseMultiple(data=methods, total_count=len(methods), page_size=len(methods))


@charges_router.get("/parameters/{method_name}", tags=["charges", "parameters"])
@inject
async def available_parameters(method_name: str, chargefw2: ChargeFW2Base = Depends(Provide[Container.chargefw2])):
    parameters: list[str] = chargefw2.get_available_parameters(method_name)
    return ResponseMultiple(data=parameters, total_count=len(parameters), page_size=len(parameters))


@charges_router.post("/info", tags=["charges", "info"])
@inject
async def info(file: UploadFile, chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service])):
    info = await chargefw2.info(file)
    return ResponseSingle(data=info)


@charges_router.post(
    "/calculate",
    tags=["charges", "calculate"],
    openapi_extra={"x-allowed-file-types": ["sdf", "mol2", "pdb", "mmcif"]},  # example
)
@inject
async def calculate_charges(
    files: list[UploadFile],
    method_name: str,
    parameters_name: str | None = None,
    chargefw2: ChargeFW2Service = Depends(Provide[Container.chargefw2_service]),
):
    charges = await chargefw2.calculate_charges(files, method_name, parameters_name)
    return ResponseMultiple(data=charges, total_count=len(charges), page_size=len(charges))
