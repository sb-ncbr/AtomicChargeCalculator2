import axios, { AxiosError } from "axios";
import { ErrorResponse } from "./types";

// TODO: move to .env?
// export const baseApiUrl = "http://147.251.245.170:8080/api/v1/web";
export const baseApiUrl = "http://localhost:8000/api/v1/web";

export const api = axios.create({
  baseURL: baseApiUrl,
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

  return "An unexpected error occured. Please try again.";
};
