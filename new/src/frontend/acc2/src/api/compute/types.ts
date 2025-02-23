export type ComputeResponse = {
  molecules: string[];
  configs: {
    method: string;
    parameters: string;
  }[];
};

export type SetupResponse = {
  computationId: string;
};
