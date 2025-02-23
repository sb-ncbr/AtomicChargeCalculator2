import { compute } from "@acc2/api/compute/compute";
import { useMutation } from "@tanstack/react-query";

type ComputationMutationData = {
  computationId: string;
  computations: { method?: string; parameters?: string }[];
};

export const useComputationMutation = () => {
  return useMutation({
    mutationFn: async ({
      computationId,
      computations,
    }: ComputationMutationData) => await compute(computationId, computations),
  });
};
