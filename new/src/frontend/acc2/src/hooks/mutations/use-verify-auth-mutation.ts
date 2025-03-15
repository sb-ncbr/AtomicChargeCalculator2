import { verifyAuth } from "@acc2/api/auth/auth";
import { useMutation } from "@tanstack/react-query";

export const useVerifyAuthMutation = () => {
  return useMutation({
    mutationFn: verifyAuth,
  });
};
