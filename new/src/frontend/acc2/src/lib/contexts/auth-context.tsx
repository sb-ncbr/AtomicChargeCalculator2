import { createContext, PropsWithChildren } from "react";

import { useAuthQuery } from "../hooks/queries/use-auth";

type AuthProviderType = {
  isAuthenticated: boolean;
  isLoading: boolean;
};

export const AuthContext = createContext<AuthProviderType>({
  isAuthenticated: false,
  isLoading: false,
});

type AuthProviderProps = PropsWithChildren;

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const verifyQuery = useAuthQuery();
  const isAuthenticated =
    verifyQuery.data?.isAuthenticated ?? !verifyQuery.isError;
  const isLoading = verifyQuery.isLoading || verifyQuery.isFetching;

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
