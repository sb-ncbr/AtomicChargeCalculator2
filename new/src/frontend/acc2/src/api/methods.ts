import { api } from "./base";
import { Response } from "./types";

export const getAvailableMethods = async (): Promise<Response<string[]>> => {
  const response = await api.get("/charges/methods");
  return response.data;
};

export type SuitableMethods = {
  methods: string[];
  parameters: {
    [key: string]: string[];
  };
};

export const getSuitableMethods = async (
  computationId: string
): Promise<Response<SuitableMethods>> => {
  const response = await api.post(
    "/charges/methods",
    {},
    { params: { computation_id: computationId } }
  );
  return response.data;
};
