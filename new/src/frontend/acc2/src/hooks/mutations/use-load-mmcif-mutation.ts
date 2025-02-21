import { baseApiUrl } from "@acc2/api/base";
import { useMutation } from "@tanstack/react-query";
import MolstarPartialCharges from "molstar-partial-charges";

export const useLoadMmcifMutation = (
  molstar: MolstarPartialCharges,
  computationId: string
) => {
  return useMutation({
    mutationFn: async ({ molecule = "" }: { molecule?: string }) => {
      await molstar.load(
        `${baseApiUrl}/charges/${computationId}/mmcif?molecule=${molecule}`,
        "mmcif",
        "ACC2"
      );
    },
    onError: (error) => console.error("Unable to load structure.", error),
  });
};
