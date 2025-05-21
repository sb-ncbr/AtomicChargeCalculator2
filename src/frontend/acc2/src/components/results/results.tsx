import { handleApiError } from "@acc2/api/base";
import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import MolstarPartialCharges from "@acc2/lib/viewer/viewer";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

import { Busy } from "../shared/busy";
import { ControlsWrapper } from "./controls/controls-wrapper";
import { MolstarWrapper } from "./molstar-wrapper";

export type ResultsProps = {
  computationId: string;
};

export const Results = ({ computationId }: ResultsProps) => {
  const navigate = useNavigate();
  const { getMoleculesMutation } = useComputationMutations();

  const [molstar, setMolstar] = useState<MolstarPartialCharges>();
  const [molecules, setMolecules] = useState<string[]>([]);

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

      <ScrollArea type="auto" className="relative">
        <h2 className="w-4/5 mx-auto max-w-content mt-8 text-3xl text-primary font-bold mb-2 sm:text-5xl">
          Computational Results
        </h2>
        {molstar && (
          <ControlsWrapper
            computationId={computationId}
            molecules={molecules}
            molstar={molstar}
          />
        )}
        <MolstarWrapper setMolstar={setMolstar} />
      </ScrollArea>
    </main>
  );
};
