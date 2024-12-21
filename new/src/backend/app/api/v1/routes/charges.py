import asyncio
from fastapi import Depends, UploadFile
from fastapi.routing import APIRouter
from core.integrations.chargefw2.base import ChargeFW2Base
from core.dependency_injection.container import Container
from dependency_injector.wiring import inject, Provide
from api.v1.schemas.response import ResponseMultiple
from services.chargefw2 import ChargeFW2Service

charges_router = APIRouter(prefix="/charges", tags=["charges"])

queue = asyncio.Queue()

@charges_router.get("/methods", tags=["charges", "methods"])
@inject
async def available_methods(chargefw2: ChargeFW2Base = Depends(Provide[Container.chargefw2])):
    methods: list[str] = chargefw2.get_available_methods()
    return ResponseMultiple(data=methods, total_count=len(methods), page_size=len(methods))


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
    return await chargefw2.calculate_charges(files, method_name, parameters_name)
