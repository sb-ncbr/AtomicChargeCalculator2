import { api } from "./base";
import { Response } from "./types";

export type SetupResponse = {
  computationId: string;
};

export const setup = async (
  files: FileList
): Promise<Response<SetupResponse>> => {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const response = await api.postForm("/charges/setup", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export type ComputeResponse = {
  molecules: string[];
  configs: {
    method: string;
    parameters: string;
  }[];
};

export const compute = async (
  computationId: string,
  computations: { method?: string; parameters?: string }[]
): Promise<Response<ComputeResponse>> => {
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

  const response = await api.post(`/charges/${computationId}/calculate`, data, {
    params: {
      response_format: "none",
    },
  });
  return response.data;
};

export const getMolecules = async (
  computationId: string
): Promise<Response<string[]>> => {
  const response = await api.get(`/charges/${computationId}/molecules`);
  return response.data;
};
