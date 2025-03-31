import { Files } from "@acc2/components/files/files";
import { useAuth } from "@acc2/hooks/queries/use-auth";
import { useTitle } from "@acc2/hooks/use-title";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

export const FilesPage = () => {
  useTitle("Files");

  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      toast.error("You need to login to view files.");
      navigate("/");
    }
  }, [loading, isAuthenticated, navigate]);

  return <Files />;
};
