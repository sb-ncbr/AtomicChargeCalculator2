import { downloadCalculation } from "@acc2/api/files/files";
import { useMutation } from "@tanstack/react-query";

export const useCalculationDownloadMutation = () => {
  return useMutation({
    mutationFn: downloadCalculation,
  });
};
