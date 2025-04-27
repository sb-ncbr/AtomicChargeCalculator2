import { api } from "../base";
import { ApiResponse } from "../types";
import { Parameters } from "./types";

export const getAvailableParameters = async (
  method: string
): Promise<Parameters[]> => {
  const response = await api.get<ApiResponse<Parameters[]>>(
    `/charges/parameters/${method}/available`
  );

  if (!response.data.success) {
    throw new Error(response.data.message ?? "Something went wrong.");
  }

  return response.data.data;
};
