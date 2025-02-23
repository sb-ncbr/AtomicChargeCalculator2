import { getMolecules } from "@acc2/api/compute/compute";
import { useMutation } from "@tanstack/react-query";

export const useMoleculesMutation = () => {
  return useMutation({
    mutationFn: getMolecules,
  });
};
