import { handleApiError } from "@acc2/api/base";
import { getFiles, getQuota } from "@acc2/api/files/files";
import { FilesFilters } from "@acc2/api/types";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

export const useFilesQuery = (filters: FilesFilters) => {
  return useQuery({
    queryKey: ["files", "list"],
    queryFn: async () => {
      try {
        return await getFiles(filters);
      } catch (error) {
        toast.error(handleApiError(error));
        throw error;
      }
    },
    retryDelay: 5000,
  });
};

export const useQuotaQuery = () => {
  return useQuery({
    queryKey: ["files", "quota"],
    queryFn: getQuota,
  });
};
