import { useVerifyAuthMutation } from "@acc2/hooks/mutations/use-verify-auth-mutation";
import { createContext, PropsWithChildren, useEffect, useState } from "react";

type AuthProviderType = {
  isAuthenticated: boolean;
  loading: boolean;
  checkAuthStatus: () => Promise<void> | void;
};

export const AuthContext = createContext<AuthProviderType>({
  isAuthenticated: false,
  loading: false,
  checkAuthStatus: () => {},
});

type AuthProviderProps = PropsWithChildren;

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const verifyAuthMutation = useVerifyAuthMutation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuthStatus = async () => {
    await verifyAuthMutation.mutateAsync(undefined, {
      onError: () => setIsAuthenticated(false),
      onSuccess: (data) => setIsAuthenticated(data.isAuthenticated),
    });
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        loading: verifyAuthMutation.isPending,
        checkAuthStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
