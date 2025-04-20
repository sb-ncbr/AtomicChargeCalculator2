import { api } from "../base";
import { ApiResponse } from "../types";
import { AdvancedSettings, ComputationConfig } from "./types";

export const setup = async (
  fileHashes: string[],
  settings?: AdvancedSettings
): Promise<string> => {
  const response = await api.post<ApiResponse<string>>("/charges/setup", {
    file_hashes: fileHashes,
    ...settingsToParams(settings),
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
    file_hashes: fileHashes,
    configs: configs.map((comp) => ({
      method: comp.method || null,
      parameters: comp.parameters || null,
    })),
    ...settingsToParams(settings),
  };

  const response = await api.post<ApiResponse<string>>(
    `/charges/calculate`,
    body,
    {
      params: {
        response_format: "none",
        ...(computationId ? { computation_id: computationId } : {}),
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

const settingsToParams = (settings?: AdvancedSettings) => {
  if (!settings) {
    return {};
  }

  return {
    settings: {
      read_hetatm: settings.readHetatm,
      ignore_water: settings.ignoreWater,
      permissive_types: settings.permissiveTypes,
    },
  };
};
