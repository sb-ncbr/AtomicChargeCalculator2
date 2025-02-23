import { getAvailableMethods } from "@acc2/api/methods/methods";
import { useQuery } from "@tanstack/react-query";

export const useAvailableMethodsQuery = () => {
  return useQuery({
    queryKey: ["available-methods"],
    queryFn: getAvailableMethods,
  });
};
