import { verifyAuth } from "@acc2/api/auth/auth";
import { useMutation } from "@tanstack/react-query";

export const useAuthMutations = () => {
  const verifyMutation = useMutation({
    mutationFn: verifyAuth,
  });

  return { verifyMutation };
};
