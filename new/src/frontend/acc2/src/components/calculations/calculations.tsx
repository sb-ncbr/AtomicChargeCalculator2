import { useEffect, useState } from "react";
import { Calculation } from "./calculation";
import { useCalculationsMutation } from "@acc2/hooks/mutations/use-calculations-mutation";
import {
  CalculationsFilters,
  isValidCalculationOrderField,
  isValidOrderDirection,
  PagedData,
} from "@acc2/api/types";
import { toast } from "sonner";
import { handleApiError } from "@acc2/api/base";
import { CalculationPreview } from "@acc2/api/calculations/types";
import { useSearchParams } from "react-router";
import { Paginator } from "../ui/paginator";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../ui/select";
import { SelectValue } from "@radix-ui/react-select";
import { Button } from "../ui/button";
import { ArrowDownZA, ArrowUpZA } from "lucide-react";
import { Busy } from "../ui/busy";

export const Calculations = () => {
  const calculationMutation = useCalculationsMutation();
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

  const [calculations, setCalculations] = useState<
    PagedData<CalculationPreview>
  >({
    items: [],
    page: filters.page,
    pageSize: filters.pageSize,
    totalCount: 0,
    totalPages: 1,
  });

  const getCalculations = async () => {
    setSearchParams(
      new URLSearchParams({
        page: `${filters.page}`,
        pageSize: `${filters.pageSize}`,
        order: `${filters.order}`,
        orderBy: `${filters.orderBy}`,
      })
    );
    await calculationMutation.mutateAsync(filters, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: (data) => setCalculations(data),
    });
  };

  useEffect(() => {
    getCalculations();
  }, [filters]);

  return (
    <main className="min-h-main w-full max-w-content mx-auto flex flex-col p-4 relative">
      <Busy isBusy={calculationMutation.isPending}>Loading Calculations</Busy>
      <h2 className="text-3xl text-primary font-bold mb-2 md:text-5xl">
        Calculations
      </h2>

      <div className="my-2 flex justify-end items-center gap-2">
        <Select
          defaultValue="created_at"
          onValueChange={(orderBy) => {
            if (!isValidCalculationOrderField(orderBy)) {
              return;
            }
            setFilters((filters) => ({ ...filters, orderBy: orderBy }));
          }}
        >
          <SelectTrigger className="w-[180px] border-2">
            <SelectValue placeholder="Order By" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at">Date</SelectItem>
          </SelectContent>
        </Select>
        <Button
          onClick={() =>
            setFilters((filters) => ({
              ...filters,
              order: filters.order === "asc" ? "desc" : "asc",
            }))
          }
        >
          {filters.order === "asc" && <ArrowUpZA />}
          {filters.order === "desc" && <ArrowDownZA />}
        </Button>
      </div>
      {calculations.items.length === 0 && (
        <div className="grid place-content-center grow">
          <span className="font-bold text-2xl">No calculations to show.</span>
        </div>
      )}
      {calculations.items.length > 0 && (
        <>
          {calculations.items.map((calculation, index) => (
            <Calculation
              key={index}
              calculation={calculation}
              className="mb-2"
            />
          ))}
          <Paginator
            page={calculations.page}
            pageSize={calculations.pageSize}
            totalPages={calculations.totalPages}
            onPageChange={({ page, pageSize }) => {
              setFilters((filters) => ({ ...filters, page, pageSize }));
            }}
            className="mt-auto"
          />
        </>
      )}
    </main>
  );
};
