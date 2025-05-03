import { isValidCalculationOrderField } from "@acc2/api/types";
import { useCalculationFilters } from "@acc2/lib/hooks/filters/use-calculation-filters";
import { useCalculationsQuery } from "@acc2/lib/hooks/queries/use-calculations";
import { useQuotaQuery } from "@acc2/lib/hooks/queries/use-files";
import { ArrowDownZA, ArrowUpZA } from "lucide-react";
import { useEffect } from "react";

import { Busy } from "../shared/busy";
import { Paginator } from "../shared/paginator";
import { QuotaProgress } from "../shared/quota-progress";
import { Button } from "../ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Calculation } from "./calculation";

export const Calculations = () => {
  const { filters, setFilters } = useCalculationFilters();

  const {
    data: quota,
    isPending: isQuotaPending,
    isError: isQuotaError,
  } = useQuotaQuery();
  const {
    data: calculations,
    refetch,
    isError: isCalculationsError,
    isPending: isCalculationsPending,
    isFetching: isCalculationsFetching,
  } = useCalculationsQuery(filters);

  useEffect(() => {
    void refetch({ cancelRefetch: false });
  }, [filters, refetch]);

  return (
    <main className="min-h-main w-full max-w-content mx-auto flex flex-col p-4">
      <Busy
        isBusy={
          isCalculationsPending || isQuotaPending || isCalculationsFetching
        }
      >
        Loading Calculations
      </Busy>
      <h2 className="text-3xl text-primary font-bold mb-2 md:text-5xl">
        Calculations
      </h2>

      <div className="w-full flex items-center gap-4">
        {quota && <QuotaProgress quota={quota} />}
      </div>

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

      {(isCalculationsError || isQuotaError) && (
        <div className="grid place-content-center grow">
          <span className="font-bold text-2xl">
            Something went wrong while fetching files.
          </span>
        </div>
      )}

      {calculations && calculations.items.length === 0 && (
        <div className="grid place-content-center grow">
          <span className="font-bold text-2xl">No calculations to show.</span>
        </div>
      )}

      {calculations && calculations.items.length > 0 && (
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
