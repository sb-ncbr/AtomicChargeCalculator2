import { api } from "../base";
import { ApiResponse } from "../types";
import { UploadResponse } from "./types";

export const upload = async (files: FileList): Promise<UploadResponse> => {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await api.postForm<ApiResponse<UploadResponse>>(
    "/files/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export const downloadCalculation = async (
  calculationId: string
): Promise<Blob> => {
  const response = await api.get<Blob>(`/files/${calculationId}/download`, {
    responseType: "blob",
  });

  if (!response.data) {
    throw Error("Unable to download calculation data.");
  }

  return response.data;
};
