import { api } from "../base";
import { ApiResponse, FilesFilters, PagedData } from "../types";
import { FileResponse, QuotaResponse, UploadResponse } from "./types";

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
  const download_path = calculationId.startsWith("examples")
    ? calculationId
    : `computation/${calculationId}`;
  const response = await api.get<Blob>(`/files/download/${download_path}`, {
    responseType: "blob",
  });

  if (!response.data) {
    throw Error("Unable to download calculation data.");
  }

  return response.data;
};

export const downloadFile = async (fileHash: string): Promise<Blob> => {
  const response = await api.get<Blob>(`/files/download/file/${fileHash}`, {
    responseType: "blob",
  });

  if (!response.data) {
    throw Error("Unable to download file.");
  }

  return response.data;
};

export const getQuota = async (): Promise<QuotaResponse> => {
  const response = await api.get<ApiResponse<QuotaResponse>>("/files/quota");

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export const getFiles = async (
  filters: FilesFilters
): Promise<PagedData<FileResponse>> => {
  const response = await api.get<ApiResponse<PagedData<FileResponse>>>(
    "/files",
    {
      params: {
        page: filters.page,
        page_size: filters.pageSize,
        order: filters.order,
        order_by: filters.orderBy,
        search: filters.search,
      },
    }
  );

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export const deleteFile = async (fileHash: string): Promise<void> => {
  const response = await api.delete<ApiResponse<void>>(`/files/${fileHash}`);

  if (!response.data.success) {
    throw new Error(response.data.message);
  }
};
