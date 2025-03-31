import { handleApiError } from "@acc2/api/base";
import { getCalculations } from "@acc2/api/calculations/calculations";
import { CalculationsFilters } from "@acc2/api/types";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

export const useCalculationsQuery = (filters: CalculationsFilters) => {
  return useQuery({
    queryKey: ["calculations", "list"],
    queryFn: async () => {
      try {
        return await getCalculations(filters);
      } catch (error) {
        toast.error(handleApiError(error));
        throw error;
      }
    },
    retryDelay: 5000,
  });
};
