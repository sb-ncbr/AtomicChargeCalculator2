import axios, { AxiosError } from "axios";

import { ErrorResponse } from "./types";

export const baseApiUrl = import.meta.env.VITE_BASE_API_URL;

if (!baseApiUrl) {
  throw new Error("BASE_API_URL environment variable is not defined.");
}

export const api = axios.create({
  baseURL: baseApiUrl,
  withCredentials: true,
});

export const handleApiError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    const responseError: AxiosError<ErrorResponse> = error;

    if (responseError.response?.data) {
      return responseError.response.data.message;
    }

    if (responseError.code === "ERR_NETWORK") {
      return "Network error. Unable to connect to server.";
    }

    if (responseError.code === "ECONNABORTED") {
      return "Request timed out. Please try again.";
    }
  }

  console.log(error);

  return "An unexpected error occured. Please try again.";
};
