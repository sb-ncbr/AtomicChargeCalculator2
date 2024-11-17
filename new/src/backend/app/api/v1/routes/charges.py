import aiofiles
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.routing import APIRouter
from core.integrations.chargefw2.base import ChargeFW2Base
from core.dependency_injection.container import Container
from dependency_injector.wiring import inject, Provide
from api.v1.schemas.response import ResponseMultiple, ResponseSingle

charges_router = APIRouter(prefix="/charges", tags=["charges"])


@charges_router.get("/methods", tags=["charges", "methods"])
@inject
async def available_methods(chargefw2: ChargeFW2Base = Depends(Provide[Container.chargefw2])):
    methods: list[str] = chargefw2.get_available_methods()
    return ResponseMultiple(data=methods, total_count=len(methods), page_size=len(methods))


# Testing purposes
@charges_router.post(
    "/file-upload",
    openapi_extra={"x-allowed-file-types": ["sdf", "mol2", "pdb", "cif"]},  # example
)
async def file_upload(file: UploadFile):
    path: str = f"/tmp/uploads/{file.filename}"
    try:
        async with aiofiles.open(path, "wb") as out_file:
            chunk_size = 1024
            while content := await file.read(chunk_size):
                await out_file.write(content)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while uploading file."
        )
    return ResponseSingle(data=path)
