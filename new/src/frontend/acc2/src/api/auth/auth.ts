import { api } from "../base";
import { ApiResponse } from "../types";
import { VerifyAuthResponse } from "./types";

export const verifyAuth = async () => {
  const response =
    await api.get<ApiResponse<VerifyAuthResponse>>("/auth/verify");

  if (!response.data.success) {
    throw Error(response.data.message);
  }

  return response.data.data;
};
