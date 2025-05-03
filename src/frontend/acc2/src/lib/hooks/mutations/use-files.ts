import { deleteFile, downloadFile, upload } from "@acc2/api/files/files";
import { useMutation } from "@tanstack/react-query";

export const useFileDownloadMutation = () => {
  return useMutation({
    mutationFn: downloadFile,
  });
};

export const useFileMutations = () => {
  const fileDeleteMutation = useMutation({
    mutationFn: deleteFile,
  });

  const fileUploadMutation = useMutation({
    mutationFn: upload,
  });

  const fileDownloadMutation = useMutation({
    mutationFn: downloadFile,
  });

  return {
    fileDeleteMutation,
    fileUploadMutation,
    fileDownloadMutation,
  };
};
