import { handleApiError } from "@acc2/api/base";
import { getCalculations } from "@acc2/api/calculations/calculations";
import {
  getAvailableMethods,
  getSuitableMethods,
} from "@acc2/api/methods/methods";
import { getAvailableParameters } from "@acc2/api/parameters/parameters";
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

export const useSuitableMethodsQuery = (computationId: string) => {
  return useQuery({
    queryKey: ["suitable-methods", computationId],
    queryFn: async () => await getSuitableMethods(computationId),
  });
};

export const useAvailableMethodsQuery = () => {
  return useQuery({
    queryKey: ["available-methods"],
    queryFn: async () => await getAvailableMethods(),
    staleTime: Infinity,
  });
};

export const useAvailableParametersQuery = (method: string) => {
  return useQuery({
    queryKey: ["available-parameters", method],
    queryFn: async () => {
      if (method) {
        return await getAvailableParameters(method);
      }

      return [];
    },
    staleTime: Infinity,
    refetchOnMount: false,
  });
};
