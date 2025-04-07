import { HTMLAttributes, useEffect, useState } from "react";
import { Card } from "../../ui/card";
import { Separator } from "../../ui/separator";
import MolstarPartialCharges from "molstar-partial-charges";
import { MolstarViewControls } from "./view-controls";
import { MolstarColoringControls } from "./coloring-controls";
import { MolstarChargesetControls } from "./chargeset-controls";
import { MolstarStructureControls } from "./structure-controls";
import { useBusyContext } from "@acc2/lib/hooks/contexts/use-busy-context";
import { useControlsContext } from "@acc2/lib/hooks/contexts/use-controls-context";
import { toast } from "sonner";
import { handleApiError } from "@acc2/api/base";
import { Button } from "@acc2/components/ui/button";
import { downloadBlob } from "@acc2/lib/utils";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";

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

  const { loadMmcifMutation, downloadMutation } = useComputationMutations();

  const [mmcifLoaded, setMmcifLoaded] = useState<boolean>(false);
  const { addBusy, removeBusy } = useBusyContext();

  const [names, setNames] = useState({ method: "", params: "" });

  const loadMolecule = async (molecule: string) => {
    addBusy();
    await loadMmcifMutation.mutateAsync(
      { molstar, computationId, molecule },
      {
        onError: (error) => toast.error(handleApiError(error)),
        onSuccess: () => setMmcifLoaded(true),
      }
    );

    await molstar.color.relative();
    context.set.methodNames(molstar.charges.getMethodNames());
    removeBusy();
  };

  const downloadCharges = async () => {
    await downloadMutation.mutateAsync(computationId, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: (data) => downloadBlob(data, "charges.zip"),
    });
  };

  useEffect(() => {
    loadMolecule(molecules?.[0]);
  }, [molstar]);

  useEffect(() => {
    const name = context.get.methodNames?.[context.get.currentTypeId - 1];
    const [method, params] = name?.split("/") ?? ["", ""];
    setNames({ method, params });
  }, [context.get.currentTypeId, context.get.methodNames]);

  // TODO get correct name for method and params
  return (
    <Card className="w-4/5 rounded-none mx-auto p-4 max-w-content mt-4 flex flex-col relative">
      <div className="flex flex-col justify-between items-stretch sm:flex-row sm:items-center">
        <div>
          <div className="flex gap-2">
            <h3 className="font-bold">Method:</h3>
            <span>{names.method}</span>
          </div>
          <div className="flex gap-2">
            <h3 className="font-bold">Parameters:</h3>
            <span>{names.params}</span>
          </div>
        </div>
        <Button
          variant={"secondary"}
          onClick={downloadCharges}
          className="mt-2 sm:mt-0"
        >
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
    </Card>
  );
};
