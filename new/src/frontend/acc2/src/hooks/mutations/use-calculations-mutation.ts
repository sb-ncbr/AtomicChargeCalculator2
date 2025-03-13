import { getCalculations } from "@acc2/api/calculations/calculations";
import { useMutation } from "@tanstack/react-query";

export const useCalculationsMutation = () => {
  return useMutation({
    mutationFn: getCalculations,
  });
};
