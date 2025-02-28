import { api } from "../base";
import { ApiResponse } from "../types";
import { ComputeResponse, SetupResponse } from "./types";

export const setup = async (files: FileList): Promise<SetupResponse> => {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await api.postForm<ApiResponse<SetupResponse>>(
    "/charges/setup",
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

export const compute = async (
  computationId: string,
  computations: { method?: string; parameters?: string }[]
): Promise<ComputeResponse> => {
  const data = computations.map((comp) => ({
    method: comp.method ?? null,
    parameters: comp.parameters ?? null,
    read_hetatm: true,
    ignore_water: false,
    permissive_types: false,
  }));

  if (computations.length === 0) {
    data.push({
      method: null,
      parameters: null,
      read_hetatm: true,
      ignore_water: false,
      permissive_types: false,
    });
  }

  const response = await api.post<ApiResponse<ComputeResponse>>(
    `/charges/${computationId}/calculate`,
    data,
    {
      params: {
        response_format: "none",
      },
    }
  );

  if (!response.data?.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export const getMolecules = async (
  computationId: string
): Promise<string[]> => {
  const response = await api.get<ApiResponse<string[]>>(
    `/charges/${computationId}/molecules`
  );

  if (!response.data.success) {
    throw Error(response.data.message);
  }

  return response.data.data;
};
