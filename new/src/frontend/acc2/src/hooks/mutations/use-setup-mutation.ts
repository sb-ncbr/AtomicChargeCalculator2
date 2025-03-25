import { setup } from "@acc2/api/compute/compute";
import { useMutation } from "@tanstack/react-query";

export const useSetupMutation = () => {
  return useMutation({
    mutationFn: setup,
  });
};
