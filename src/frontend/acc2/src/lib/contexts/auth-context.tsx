import { createContext, PropsWithChildren } from "react";

import { useAuthQuery } from "../hooks/queries/use-auth";

type AuthProviderType = {
  isAuthenticated: boolean | null;
  isLoading: boolean;
};

export const AuthContext = createContext<AuthProviderType>({
  isAuthenticated: null,
  isLoading: false,
});

type AuthProviderProps = PropsWithChildren;

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const verifyQuery = useAuthQuery();
  const isAuthenticated = verifyQuery.data?.isAuthenticated ?? null;
  const isLoading = verifyQuery.isLoading || verifyQuery.isFetching;

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
