export type CalculationPreview = {
  id: string;
  files: {
    [filename: string]: {
      totalMolecules: number;
      totalAtoms: number;
      atomTypeCounts: {
        symbol: string;
        count: number;
      }[];
    };
  };
  configs: {
    method: string;
    parameters: string;
    readHetatm: boolean;
    ignoreWater: boolean;
    permissiveTypes: boolean;
  }[];
  createdAt: string;
};
