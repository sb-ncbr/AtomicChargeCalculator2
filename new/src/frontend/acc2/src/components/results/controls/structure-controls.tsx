import { ComputeResponse } from "@acc2/api/compute";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@acc2/components/ui/select";
import { useControlsContext } from "@acc2/hooks/contexts/use-controls-context";
import MolstarPartialCharges from "molstar-partial-charges";
import { HTMLAttributes } from "react";

export type MolstarStructureControls = {
  molstar: MolstarPartialCharges;
  molecules: ComputeResponse["molecules"];
  onStructureSelect: (molecule: string) => void | Promise<void>;
} & HTMLAttributes<HTMLElement>;

export const MolstarStructureControls = ({
  molecules,
  onStructureSelect,
  molstar,
}: MolstarStructureControls) => {
  const context = useControlsContext(molstar);

  const handleSelect = async (molecule: string) => {
    await onStructureSelect(molecule);
    context.set.structure(molecule);
  };

  return (
    <div>
      <h3 className="font-bold mb-2">Structure</h3>
      <Select
        onValueChange={handleSelect}
        defaultValue={molecules[0].toUpperCase()}
      >
        <SelectTrigger className="min-w-[180px] border-2 uppercase">
          <SelectValue placeholder="Structure" />
        </SelectTrigger>
        <SelectContent>
          {molecules.map((molecule, index) => (
            <SelectItem
              key={index}
              value={molecule.toUpperCase()}
              className="uppercase"
            >
              {molecule}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
