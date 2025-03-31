import datetime
from core.models.molecule_info import MoleculeSetStats
from .base_response import BaseResponseSchema


class UploadResponse(BaseResponseSchema):
    """Response schema for uploading a file(s)."""

    file: str
    file_hash: str


class FileResponse(BaseResponseSchema):
    """Response schema for listing files."""

    file_hash: str
    file_name: str
    size: int
    stats: MoleculeSetStats
    uploaded_at: datetime.datetime


class QuotaResponse(BaseResponseSchema):
    """Response schema for getting quota."""

    used_space: int
    available_space: int
    quota: int
