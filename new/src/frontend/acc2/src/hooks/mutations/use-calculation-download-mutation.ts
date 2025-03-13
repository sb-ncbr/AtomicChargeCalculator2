import { downloadCalculation } from "@acc2/api/calculations/calculations";
import { useMutation } from "@tanstack/react-query";

export const useCalculationDownloadMutation = () => {
  return useMutation({
    mutationFn: downloadCalculation,
  });
};
