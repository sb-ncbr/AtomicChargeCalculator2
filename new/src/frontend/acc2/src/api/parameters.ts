import { api } from "./base";
import { ApiResponse } from "./types";

export const getAvailableParameters = async (
  method: string
): Promise<string[]> => {
  const response = await api.get<ApiResponse<string[]>>(
    `/charges/parameters/${method}`
  );

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};
