import { deleteCalculation } from "@acc2/api/calculations/calculations";
import { useMutation } from "@tanstack/react-query";

export const useCalculationDeleteMutation = () => {
  return useMutation({
    mutationFn: deleteCalculation,
  });
};
