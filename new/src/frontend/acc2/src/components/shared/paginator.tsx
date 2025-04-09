import { PagingFilters } from "@acc2/api/types";
import { cn } from "@acc2/lib/utils";
import { useSearchParams } from "react-router";

import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";

export type PaginatorProps = {
  page: number;
  pageSize: number;
  totalPages: number;
  onPageChange: (filters: PagingFilters) => void;
} & React.ComponentProps<"nav">;

export const Paginator = ({
  page,
  pageSize,
  totalPages,
  onPageChange,
  className,
}: PaginatorProps) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const onChange = (filters: PagingFilters) => {
    const params = new URLSearchParams(searchParams);

    Object.keys(filters).forEach((key, value) => {
      params.set(key, `${value}`);
    });

    setSearchParams(params);
    onPageChange(filters);
  };

  return (
    <Pagination className={cn(className)}>
      <PaginationContent>
        <PaginationItem className="w-32">
          {page <= 1 && (
            <PaginationPrevious
              tabIndex={-1}
              className="opacity-50 pointer-events-none"
              disabled
            />
          )}
          {page > 1 && (
            <PaginationPrevious
              onClick={() =>
                onChange({
                  page: page - 1,
                  pageSize: pageSize,
                })
              }
            />
          )}
        </PaginationItem>
        {/* Show two pages around current page (if possible) */}
        {[...new Array(5).keys()].map((i) => {
          const pageOffset = page + i - 2;
          if (pageOffset <= 0 || pageOffset > totalPages) {
            return null;
          }

          return (
            <PaginationItem key={pageOffset}>
              <PaginationLink
                isActive={pageOffset === page}
                onClick={() =>
                  onChange({
                    page: pageOffset,
                    pageSize: pageSize,
                  })
                }
              >
                {pageOffset}
              </PaginationLink>
            </PaginationItem>
          );
        })}
        <PaginationItem className="w-32">
          {totalPages > page && (
            <PaginationNext
              onClick={() =>
                onChange({
                  page: page + 1,
                  pageSize: pageSize,
                })
              }
            />
          )}
          {totalPages <= page && (
            <PaginationNext
              tabIndex={-1}
              className="opacity-50 pointer-events-none"
              disabled
            />
          )}
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
};
