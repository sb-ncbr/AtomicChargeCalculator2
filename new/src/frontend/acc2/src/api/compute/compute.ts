import { api } from "../base";
import { ApiResponse } from "../types";
import { ComputationConfig, ComputeResponse, SetupResponse } from "./types";

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
  computations: ComputationConfig[]
): Promise<ComputeResponse> => {
  const data = computations.map((comp) => ({
    method: comp.method ?? null,
    parameters: comp.parameters ?? null,
    read_hetatm: comp.readHetatm,
    ignore_water: comp.ignoreWater,
    permissive_types: comp.permissiveTypes,
  }));

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
