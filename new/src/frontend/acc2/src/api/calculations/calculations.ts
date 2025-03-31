import { api } from "../base";
import { ApiResponse, CalculationsFilters, PagedData } from "../types";
import { CalculationPreview } from "./types";

export const getCalculations = async (
  filters: CalculationsFilters
): Promise<PagedData<CalculationPreview>> => {
  const response = await api.get<ApiResponse<PagedData<CalculationPreview>>>(
    `/charges/calculations`,
    {
      params: {
        page: filters.page,
        page_size: filters.pageSize,
        order: filters.order,
        order_by: filters.orderBy,
      },
    }
  );

  if (!response.data.success) {
    throw Error(response.data.message);
  }

  return response.data.data;
};

export const deleteCalculation = async (computationId: string) => {
  const response = await api.delete(`/charges/${computationId}`);

  if (!response.data.success) {
    throw Error(response.data.message);
  }

  return response.data.data;
};
