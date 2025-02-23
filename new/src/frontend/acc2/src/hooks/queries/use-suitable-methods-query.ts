import { getSuitableMethods } from "@acc2/api/methods/methods";
import { useQuery } from "@tanstack/react-query";

export const useSuitableMethodsQuery = (computationId: string) => {
  return useQuery({
    queryKey: ["suitable-methods"],
    queryFn: async () => await getSuitableMethods(computationId),
  });
};
