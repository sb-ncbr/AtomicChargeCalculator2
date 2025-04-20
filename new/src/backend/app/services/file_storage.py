from datetime import datetime
from pathlib import Path
from typing import Literal
from db.database import SessionManager
from api.v1.schemas.file import FileResponse
from models.paging import PagedList
from services.calculation_storage import CalculationStorageService
from services.io import IOService
from services.logging.base import LoggerBase


class FileStorageService:
    """Service for manipulating files in the database and filesystem."""

    def __init__(
        self,
        logger: LoggerBase,
        io: IOService,
        session_manager: SessionManager,
        storage_service: CalculationStorageService,
    ):
        self.io = io
        self.storage_service = storage_service
        self.session_manager = session_manager
        self.logger = logger

    def get_files(
        self,
        order_by: Literal["name", "size", "uploaded_at"],
        order: Literal["asc", "desc"],
        page: int,
        page_size: int,
        search: str,
        user_id: str,
    ) -> PagedList[FileResponse]:
        workdir = self.io.get_file_storage_path(user_id)
        files = [self.io.parse_filename(Path(name).name) for name in self.io.listdir(workdir)]

        is_reverse = order == "desc"

        match order_by:
            case "name":
                files.sort(key=lambda x: x[1], reverse=is_reverse)
            case "size":
                files.sort(key=lambda x: self.io.get_file_size(x[0], user_id), reverse=is_reverse)
            case "uploaded_at" | _:
                files.sort(
                    key=lambda x: self.io.get_last_modification(x[0], user_id), reverse=is_reverse
                )

        if search != "":
            files = [file for file in files if search.casefold() in file[1].casefold()]

        page_start = (page - 1) * page_size
        page_end = page * page_size

        with self.session_manager.session() as session:
            items = [
                FileResponse(
                    file_name=name,
                    file_hash=file_hash,
                    size=self.io.get_file_size(file_hash, user_id) or 0,
                    stats=self.storage_service.get_info(session, file_hash),
                    uploaded_at=self.io.get_last_modification(file_hash, user_id) or datetime.min,
                )
                for [file_hash, name] in files[page_start:page_end]
            ]

            data = PagedList(page=page, page_size=page_size, total_count=len(files), items=items)
            return data
