import { api } from "../base";
import { ApiResponse } from "../types";
import { AdvancedSettings, ComputationConfig } from "./types";

export const setup = async (
  fileHashes: string[],
  settings?: AdvancedSettings
): Promise<string> => {
  const response = await api.post<ApiResponse<string>>("/charges/setup", {
    fileHashes,
    ...(settings ? { settings } : {}),
  });

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export const compute = async (
  fileHashes: string[],
  configs: ComputationConfig[],
  settings?: AdvancedSettings,
  computationId?: string
): Promise<string> => {
  const body = {
    fileHashes,
    configs: configs.map((comp) => ({
      method: comp.method || null,
      parameters: comp.parameters || null,
    })),
    ...(computationId ? { computation_id: computationId } : {}),
    ...(settings ? { settings } : {}),
  };

  const response = await api.post<ApiResponse<string>>(
    `/charges/calculate`,
    body,
    {
      params: {
        response_format: "none",
      },
    }
  );

  if (!response.data?.success) {
    throw new Error(response.data.message ?? "Something went wrong.");
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
    throw Error(response.data.message ?? "Something went wrong.");
  }

  return response.data.data;
};
