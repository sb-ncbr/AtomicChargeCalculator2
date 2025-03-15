import { Calculations } from "@acc2/components/calculations/calculations";
import { useAuth } from "@acc2/hooks/queries/use-auth";
import { useTitle } from "@acc2/hooks/use-title";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

export const CalculationsPage = () => {
  useTitle("Calculations");

  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      toast.error("You need to login to view calculations.");
      navigate("/");
    }
  }, [loading]);

  return <Calculations />;
};
