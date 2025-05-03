export type SetupResponse = {
  computationId: string;
};

export type ComputationConfig = {
  method?: string;
  parameters?: string;
};

export type AdvancedSettings = {
  readHetatm: boolean;
  ignoreWater: boolean;
  permissiveTypes: boolean;
};
