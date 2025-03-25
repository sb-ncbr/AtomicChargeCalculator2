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
