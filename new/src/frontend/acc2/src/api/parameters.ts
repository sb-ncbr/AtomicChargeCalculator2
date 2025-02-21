import { api } from "./base";
import { Response } from "./types";

export const getAvailableParameters = async (
  method: string
): Promise<Response<string[]>> => {
  const response = await api.get(`/charges/parameters/${method}`);
  return response.data;
};
