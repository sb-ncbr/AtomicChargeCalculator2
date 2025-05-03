import { Files } from "@acc2/components/files/files";
import { useAuth } from "@acc2/lib/hooks/queries/use-auth";
import { useTitle } from "@acc2/lib/hooks/use-title";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

export const FilesPage = () => {
  useTitle("Files");

  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      toast.error("You need to login to view files.");
      void navigate("/");
    }
  }, [isLoading, isAuthenticated, navigate]);

  return <Files />;
};
