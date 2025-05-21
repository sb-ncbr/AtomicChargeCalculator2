import { handleApiError } from "@acc2/api/base";
import { Busy } from "@acc2/components/shared/busy";
import { Button } from "@acc2/components/ui/button";
import { useControlsContext } from "@acc2/lib/hooks/contexts/use-controls-context";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import {
  useAvailableMethodsQuery,
  useAvailableParametersQuery,
} from "@acc2/lib/hooks/queries/use-calculations";
import { downloadBlob } from "@acc2/lib/utils";
import MolstarPartialCharges from "@acc2/lib/viewer/viewer";
import { HTMLAttributes, useEffect, useState } from "react";
import { toast } from "sonner";

import { Separator } from "../../ui/separator";
import { MolstarChargesetControls } from "./chargeset-controls";
import { MolstarColoringControls } from "./coloring-controls";
import { MolstarStructureControls } from "./structure-controls";
import { MolstarViewControls } from "./view-controls";

export type ControlsProps = {
  computationId: string;
  molstar: MolstarPartialCharges;
  molecules: string[];
} & HTMLAttributes<HTMLElement>;

export const Controls = ({
  computationId,
  molstar,
  molecules,
}: ControlsProps) => {
  const context = useControlsContext(molstar);

  const [mmcifLoaded, setMmcifLoaded] = useState<boolean>(false);

  const [names, setNames] = useState({ method: "", params: "" });

  const { data: availableMethods, isPending: isMethodsPending } =
    useAvailableMethodsQuery();
  const {
    data: availableParameters,
    refetch: refetchAvailableParameters,
    isRefetching: isParametersPending,
  } = useAvailableParametersQuery(names.method);
  const { loadMmcifMutation, downloadMutation } = useComputationMutations();

  const loadMolecule = async (molecule: string) => {
    await loadMmcifMutation.mutateAsync(
      { molstar, computationId, molecule },
      {
        onError: (error) => toast.error(handleApiError(error)),
        onSuccess: async () => {
          await Promise.all([
            await context.set.viewType(context.get.viewType),
            await context.set.coloringType("charges-relative"),
          ]);

          context.set.methodNames(molstar.charges.getMethodNames());
          setMmcifLoaded(true);
        },
      }
    );
  };

  const downloadCharges = async () => {
    await downloadMutation.mutateAsync(computationId, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: (data) => downloadBlob(data, "charges.zip"),
    });
  };

  useEffect(() => {
    void loadMolecule(molecules?.[0]);
  }, [molstar]);

  useEffect(() => {
    const name = context.get.methodNames?.[context.get.currentTypeId - 1];
    const [method, params] = name?.split("/") ?? ["", ""];
    setNames((prev) => {
      if (method && method !== prev.method) {
        void refetchAvailableParameters();
      }
      return { method, params };
    });
  }, [context.get.currentTypeId, context.get.methodNames]);

  return (
    <>
      <Busy isBusy={isMethodsPending || isParametersPending} />
      <div className="flex flex-col justify-between items-stretch sm:flex-row sm:items-center">
        <div>
          <div className="flex gap-2">
            <h3 className="font-bold">Method:</h3>
            <span>
              {availableMethods?.find((m) => m.internalName === names.method)
                ?.name || names.method}
            </span>
          </div>
          <div className="flex gap-2">
            <h3 className="font-bold">Parameters:</h3>
            <span>
              {availableParameters?.find((p) => p.internalName === names.params)
                ?.fullName || names.params}
            </span>
          </div>
        </div>
        <Button
          variant={"secondary"}
          onClick={downloadCharges}
          className="mt-2 sm:mt-0 relative"
          disabled={downloadMutation.isPending}
        >
          <Busy isBusy={downloadMutation.isPending} className="text-black" />
          Download
        </Button>
      </div>
      <Separator className="my-4" />
      {mmcifLoaded && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xxl:grid-cols-3 gap-4">
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
            <MolstarStructureControls
              molstar={molstar}
              molecules={molecules}
              onStructureSelect={loadMolecule}
            />
            <MolstarChargesetControls molstar={molstar} />
          </div>
          <MolstarViewControls molstar={molstar} />
          <MolstarColoringControls molstar={molstar} />
        </div>
      )}
    </>
  );
};
