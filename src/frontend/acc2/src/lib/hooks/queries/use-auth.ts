import { verifyAuth } from "@acc2/api/auth/auth";
import { AuthContext } from "@acc2/lib/contexts/auth-context";
import { useQuery } from "@tanstack/react-query";
import { useContext } from "react";

export const useAuthQuery = () => {
  return useQuery({
    queryKey: ["auth", "verify"],
    queryFn: verifyAuth,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
  });
};

export const useAuth = () => useContext(AuthContext);
