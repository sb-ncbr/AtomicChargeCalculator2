import { handleApiError } from "@acc2/api/base";
import { MolstarColoringType } from "@acc2/components/results/controls/coloring-controls";
import { MolstarViewType } from "@acc2/components/results/controls/view-controls";
import { MolStarWrapper } from "@acc2/components/results/molstar";
import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { ControlsContextProvider } from "@acc2/lib/contexts/controls-context";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import MolstarPartialCharges from "molstar-partial-charges";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

import { Busy } from "../shared/busy";
import { ControlsWrapper } from "./controls/controls-wrapper";

export type ResultsProps = {
  computationId: string;
};

export const Results = ({ computationId }: ResultsProps) => {
  const navigate = useNavigate();
  const { getMoleculesMutation } = useComputationMutations();

  const [molstar, setMolstar] = useState<MolstarPartialCharges>();
  const [molecules, setMolecules] = useState<string[]>([]);

  // controls
  const [currentTypeId, setCurrentTypeId] = useState<number>(1);
  const [structure, setStructure] = useState<string>(molecules[0]);
  const [coloringType, setColoringType] =
    useState<MolstarColoringType>("charges-relative");
  const [maxValue, setMaxValue] = useState<number>(0);
  const [viewType, setViewType] = useState<MolstarViewType>(
    molstar?.type.isDefaultApplicable() ? "cartoon" : "balls-and-sticks"
  );
  const [methodNames, setMethodNames] = useState<(string | undefined)[]>([]);

  const loadMolecules = async () => {
    // make this a query
    await getMoleculesMutation.mutateAsync(computationId, {
      onError: (error) => {
        toast.error(handleApiError(error));
        void navigate("/");
      },
      onSuccess: (molecules) => setMolecules(molecules),
    });
  };

  useEffect(() => {
    void loadMolecules();
  }, []);

  return (
    <main className="mx-auto w-full selection:text-white selection:bg-primary mb-8 relative">
      <Busy isBusy={getMoleculesMutation.isPending || !molstar} fullscreen />
      <ControlsContextProvider
        value={{
          currentTypeId,
          setCurrentTypeId,
          coloringType,
          setColoringType,
          maxValue,
          setMaxValue,
          structure,
          setStructure,
          viewType,
          setViewType,
          methodNames,
          setMethodNames,
        }}
      >
        <ScrollArea type="auto" className="relative">
          <h2 className="w-4/5 mx-auto max-w-content mt-8 text-3xl text-primary font-bold mb-2 sm:text-5xl">
            Computational Results
          </h2>
          <ControlsWrapper
            computationId={computationId}
            molecules={molecules}
            molstar={molstar}
          />
          <MolStarWrapper setMolstar={setMolstar} />
        </ScrollArea>
      </ControlsContextProvider>
    </main>
  );
};
