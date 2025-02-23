import { getAvailableParameters } from "@acc2/api/parameters/parameters";
import { useMutation } from "@tanstack/react-query";

export const useAvailableParametersMutation = () => {
  return useMutation({
    mutationFn: getAvailableParameters,
  });
};
