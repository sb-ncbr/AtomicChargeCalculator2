import {
  deleteFile,
  downloadFile,
  getFiles,
  upload,
} from "@acc2/api/files/files";
import { useMutation } from "@tanstack/react-query";

export const useFilesMutation = () => {
  return useMutation({
    mutationFn: getFiles,
  });
};

export const useFileDeleteMutation = () => {
  return useMutation({
    mutationFn: deleteFile,
  });
};

export const useFileUploadMutation = () => {
  return useMutation({
    mutationFn: upload,
  });
};

export const useFileDownloadMutation = () => {
  return useMutation({
    mutationFn: downloadFile,
  });
};
