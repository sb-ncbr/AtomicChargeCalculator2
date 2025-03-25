import { upload } from "@acc2/api/files/files";
import { useMutation } from "@tanstack/react-query";

export const useFileUploadMutation = () => {
  return useMutation({
    mutationFn: upload,
  });
};
