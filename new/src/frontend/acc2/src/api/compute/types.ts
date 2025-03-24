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

export type ComputationConfig = {
  method?: string;
  parameters?: string;
  readHetatm: boolean;
  ignoreWater: boolean;
  permissiveTypes: boolean;
};
