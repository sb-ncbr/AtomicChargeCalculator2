import { api } from "../base";
import { ApiResponse } from "../types";
import { SuitableMethods } from "./types";

export const getSuitableMethods = async (
  computationId: string
): Promise<SuitableMethods> => {
  const response = await api.post<ApiResponse<SuitableMethods>>(
    `/charges/${computationId}/methods`
  );

  if (!response.data.success) {
    throw new Error(response.data.message);
  }

  return response.data.data;
};
