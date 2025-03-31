import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Router } from "./router";
import { Toaster } from "sonner";
import { AuthProvider } from "./contexts/auth-context";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      refetchOnMount: false,
    },
  },
});

export const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster richColors />
      <AuthProvider>
        <Router />
      </AuthProvider>
    </QueryClientProvider>
  );
};
