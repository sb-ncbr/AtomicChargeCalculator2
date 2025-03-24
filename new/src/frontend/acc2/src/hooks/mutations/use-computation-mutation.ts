import { compute } from "@acc2/api/compute/compute";
import { ComputationConfig } from "@acc2/api/compute/types";
import { useMutation } from "@tanstack/react-query";

type ComputationMutationData = {
  computationId: string;
  computations: ComputationConfig[];
};

export const useComputationMutation = () => {
  return useMutation({
    mutationFn: async ({
      computationId,
      computations,
    }: ComputationMutationData) => await compute(computationId, computations),
  });
};
