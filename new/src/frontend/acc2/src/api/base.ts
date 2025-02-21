import axios from "axios";

// TODO: move to .env?
export const baseApiUrl = "http://localhost:8000/api/v1/web";

export const api = axios.create({
  baseURL: baseApiUrl,
});
