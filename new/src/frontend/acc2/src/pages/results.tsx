import { MolstarColoringType } from "@acc2/components/results/controls/coloring-controls";
import { Controls } from "@acc2/components/results/controls/controls";
import { MolstarViewType } from "@acc2/components/results/controls/view-controls";
import { MolStarWrapper } from "@acc2/components/results/molstar";
import { Busy } from "@acc2/components/ui/busy";
import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { BusyContextProvider } from "@acc2/contexts/busy-context";
import { ControlsContextProvider } from "@acc2/contexts/controls-context";
import { useMoleculesMutation } from "@acc2/hooks/mutations/use-molecules-mutation";
import { useTitle } from "@acc2/hooks/use-title";
import MolstarPartialCharges from "molstar-partial-charges";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { toast } from "sonner";

export const Results = () => {
  useTitle("Results");

  const navigate = useNavigate();
  const moleculesMutation = useMoleculesMutation();

  const [searchParams, _setSearchParams] = useSearchParams();
  const [molstar, setMolstar] = useState<MolstarPartialCharges>();
  const [molecules, setMolecules] = useState<string[]>([]);
  const [busyCount, setBusyCount] = useState<number>(0);

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

  const computationId = searchParams.get("comp_id");
  if (!computationId) {
    navigate("/");
    return null;
  }

  const loadMolecules = async () => {
    const response = await moleculesMutation.mutateAsync(computationId, {
      onError: () => {
        toast.error("Unable to load computation data.");
        navigate("/");
      },
    });

    if (!response.success) {
      navigate("/");
      return;
    }
    setMolecules(response.data);
  };

  useEffect(() => {
    loadMolecules();
  }, []);

  return (
    <main
      className={
        "mx-auto w-full selection:text-white selection:bg-primary mb-8 relative"
      }
    >
      <BusyContextProvider value={{ busyCount, setBusyCount }}>
        <Busy isBusy={busyCount > 0} />
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
            {molstar && (
              <Controls
                computationId={computationId}
                molecules={molecules}
                molstar={molstar}
              />
            )}
            <MolStarWrapper setMolstar={setMolstar} />
          </ScrollArea>
        </ControlsContextProvider>
      </BusyContextProvider>
    </main>
  );
};
