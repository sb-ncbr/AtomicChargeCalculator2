import { api } from "../base";
import { ApiResponse } from "../types";
import { ComputationConfig } from "./types";

export const setup = async (fileHashes: string[]): Promise<string> => {
  const response = await api.post<ApiResponse<string>>(
    "/charges/setup",
    fileHashes
  );

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export const compute = async (
  fileHashes: string[],
  configs: ComputationConfig[],
  computationId?: string
): Promise<string> => {
  const data = configs.map((comp) => ({
    method: comp.method ?? null,
    parameters: comp.parameters ?? null,
    read_hetatm: comp.readHetatm,
    ignore_water: comp.ignoreWater,
    permissive_types: comp.permissiveTypes,
  }));

  const body = {
    file_hashes: fileHashes,
    configs: data,
  };

  const response = await api.post<ApiResponse<string>>(
    `/charges/calculate`,
    body,
    {
      params: {
        response_format: "none",
        ...(computationId ? { computation_id: computationId } : {}),
      },
      data: {
        file_hashes: fileHashes,
        configs: data,
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
