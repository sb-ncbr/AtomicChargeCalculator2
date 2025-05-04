import { api } from "../base";
import { ApiResponse } from "../types";
import { Method, SuitableMethods } from "./types";

// we don't want to show 'dummy' method on frontend
const DUMMY_KEY = "dummy";

export const getSuitableMethods = async (
  computationId: string
): Promise<SuitableMethods> => {
  const response = await api.post<ApiResponse<SuitableMethods>>(
    `/charges/${computationId}/methods/suitable`
  );

  if (!response.data.success) {
    throw new Error(response.data.message ?? "Something went wrong.");
  }

  const data = response.data.data;

  data.methods = data.methods.filter(
    (method) => method.internalName !== DUMMY_KEY
  );
  delete data.parameters[DUMMY_KEY];

  return data;
};

export const getAvailableMethods = async (): Promise<Method[]> => {
  const response = await api.get<ApiResponse<Method[]>>(
    `/charges/methods/available`
  );

  if (!response.data.success) {
    throw new Error(response.data.message ?? "Something went wrong.");
  }

  const data = response.data.data;
  const methods = data.filter((method) => method.internalName !== DUMMY_KEY);

  return methods;
};
