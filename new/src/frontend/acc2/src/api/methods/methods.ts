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

  const data = response.data.data;

  // we don't want to show 'dummy' method on frontend
  const dummyKey = "dummy";
  data.methods = data.methods.filter(
    (method) => method.internalName !== dummyKey
  );
  delete data.parameters[dummyKey];

  return data;
};
