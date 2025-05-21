import {
  CalculationsFilters,
  isValidCalculationOrderField,
  isValidOrderDirection,
} from "@acc2/api/types";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";

export const useCalculationFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<CalculationsFilters>(() => {
    const directionParam = searchParams.get("order") ?? "";
    const fieldParam = searchParams.get("orderBy") ?? "";

    return {
      order: isValidOrderDirection(directionParam) ? directionParam : "desc",
      orderBy: isValidCalculationOrderField(fieldParam)
        ? fieldParam
        : "created_at",
      page: Math.max(1, Number(searchParams.get("page") ?? 1)),
      pageSize: Math.max(1, Number(searchParams.get("pageSize") ?? 5)),
    };
  });

  useEffect(() => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set("order", filters.order);
    newParams.set("order_by", filters.orderBy);
    newParams.set("page", `${filters.page}`);
    newParams.set("page_size", `${filters.pageSize}`);

    setSearchParams(newParams);
  }, [filters]);

  return { filters, setFilters };
};
