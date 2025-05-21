"""Provides a dataclass for paging filters and a class for paged lists."""

from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


@dataclass
class PagingFilters:
    """Filters for paging."""

    page: int
    page_size: int


class PagedList[T](BaseModel):  # add BaseModel
    """
    Paged list of items.

    Turns a query into a paged list of items.
    If no (or <= 0) page or page_size are provided,
    it defaults to PagedList.DEFAULT_PAGE and PagedList.DEFAULT_PAGE_SIZE.
    """

    _DEFAULT_PAGE: int = 1
    _DEFAULT_PAGE_SIZE: int = 10

    items: list[T]
    page: int
    page_size: int
    total_count: int
    total_pages: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )

    def __init__(
        self,
        items: list[T],
        page: int = _DEFAULT_PAGE,
        page_size: int = _DEFAULT_PAGE_SIZE,
        total_count: int = 0,
        total_pages: int = 0,
    ) -> None:
        page = page if page > 0 else PagedList._DEFAULT_PAGE
        page_size = page_size if page_size > 0 else PagedList._DEFAULT_PAGE_SIZE

        total_pages = PagedList._get_total_pages(total_count, page_size)

        super().__init__(
            items=items,
            page=page,
            page_size=page_size,
            total_count=total_count,
            total_pages=total_pages,
        )

    @staticmethod
    def _get_total_pages(total_count: int, page_size: int) -> int:
        """
        Calculate the total number of pages.

        Returns:
            int: Total number of pages.
        """
        return (total_count + page_size - 1) // page_size
