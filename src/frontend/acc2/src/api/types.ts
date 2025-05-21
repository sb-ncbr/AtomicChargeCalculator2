export type SuccessResponse<T> = {
  success: true;
  data: T;
};

export type ErrorResponse = {
  success: false;
  message: string;
};

export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

export type PagedData<T> = {
  items: T[];
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
};

export type PagingFilters = {
  page: number;
  pageSize: number;
};

export type OrderFilters<T extends string> = {
  order: OrderDirection;
  orderBy: T;
};

// Type for order direction query param
const orderDirections = ["asc", "desc"] as const;

type OrderDirection = (typeof orderDirections)[number];

export const isValidOrderDirection = (
  value: string
): value is OrderDirection => {
  return orderDirections.includes(value as OrderDirection);
};

// Type for order fields used with calculations
const calculationsOrderFields = ["created_at"] as const;
type CalculationsOrderFields = (typeof calculationsOrderFields)[number];

export type CalculationsFilters = PagingFilters &
  OrderFilters<CalculationsOrderFields>;

export const isValidCalculationOrderField = (
  value: string
): value is CalculationsOrderFields => {
  return calculationsOrderFields.includes(value as CalculationsOrderFields);
};

const filesOrderFields = ["name", "size", "uploaded_at"] as const;
type FilesOrderFields = (typeof filesOrderFields)[number];

export type FilesFilters = {
  search?: string;
} & PagingFilters &
  OrderFilters<FilesOrderFields>;

export const isValidFilesOrderField = (
  value: string
): value is FilesOrderFields => {
  return filesOrderFields.includes(value as FilesOrderFields);
};
