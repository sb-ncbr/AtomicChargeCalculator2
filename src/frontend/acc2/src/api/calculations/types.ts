export type CalculationPreview = {
  id: string;
  files: { [filename: string]: MoleculeSetStats };
  configs: {
    method: string;
    parameters: string;
  }[];
  settings: {
    readHetatm: boolean;
    ignoreWater: boolean;
    permissiveTypes: boolean;
  };
  createdAt: string;
};

export type MoleculeSetStats = {
  totalMolecules: number;
  totalAtoms: number;
  atomTypeCounts: {
    symbol: string;
    count: number;
  }[];
};
