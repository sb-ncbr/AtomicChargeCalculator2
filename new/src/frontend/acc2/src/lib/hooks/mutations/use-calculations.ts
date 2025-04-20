import { baseApiUrl } from "@acc2/api/base";
import { deleteCalculation } from "@acc2/api/calculations/calculations";
import { compute, getMolecules, setup } from "@acc2/api/compute/compute";
import { AdvancedSettings, ComputationConfig } from "@acc2/api/compute/types";
import { downloadCalculation } from "@acc2/api/files/files";
import { useMutation } from "@tanstack/react-query";
import MolstarPartialCharges from "molstar-partial-charges";

type SetupMutationData = {
  fileHashes: string[];
  settings?: AdvancedSettings;
};

type ComputationMutationData = {
  computationId?: string;
  fileHashes: string[];
  configs: ComputationConfig[];
  settings?: AdvancedSettings;
};

type LoadMmcifMutationData = {
  molstar: MolstarPartialCharges;
  computationId: string;
  molecule?: string;
};

export const useComputationMutations = () => {
  const deleteMutation = useMutation({
    mutationFn: deleteCalculation,
  });

  const downloadMutation = useMutation({
    mutationFn: downloadCalculation,
  });

  const getMoleculesMutation = useMutation({
    mutationFn: getMolecules,
  });

  const setupMutation = useMutation({
    mutationFn: async ({ fileHashes, settings }: SetupMutationData) =>
      await setup(fileHashes, settings),
  });

  const computeMutation = useMutation({
    mutationFn: async ({
      computationId,
      fileHashes,
      settings,
      configs,
    }: ComputationMutationData) =>
      await compute(fileHashes, configs, settings, computationId),
  });

  const loadMmcifMutation = useMutation({
    mutationFn: async ({
      molstar,
      computationId,
      molecule = "",
    }: LoadMmcifMutationData) => {
      const search = molecule ? `?molecule=${molecule}` : "";
      await molstar.load(
        `${baseApiUrl}/charges/${computationId}/mmcif${search}`,
        "mmcif",
        "ACC2"
      );
    },
  });

  return {
    deleteMutation,
    downloadMutation,
    getMoleculesMutation,
    setupMutation,
    computeMutation,
    loadMmcifMutation,
  };
};
