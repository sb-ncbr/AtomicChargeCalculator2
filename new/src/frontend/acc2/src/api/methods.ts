import { api } from "./base";
import { ApiResponse } from "./types";

export const getAvailableMethods = async (): Promise<string[]> => {
  const response = await api.get<ApiResponse<string[]>>("/charges/methods");

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};

export type SuitableMethods = {
  methods: string[];
  parameters: {
    [key: string]: string[];
  };
};

export const getSuitableMethods = async (
  computationId: string
): Promise<SuitableMethods> => {
  const response = await api.post<ApiResponse<SuitableMethods>>(
    "/charges/methods",
    {},
    { params: { computation_id: computationId } }
  );

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};
