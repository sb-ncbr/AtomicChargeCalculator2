import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@acc2/components/ui/select";
import { useControlsContext } from "@acc2/lib/hooks/contexts/use-controls-context";
import MolstarPartialCharges from "@acc2/lib/viewer/viewer";
import { HTMLAttributes } from "react";

export type MolstarChargesetControlsProps = {
  molstar: MolstarPartialCharges;
} & HTMLAttributes<HTMLElement>;

export const MolstarChargesetControls = ({
  molstar,
}: MolstarChargesetControlsProps) => {
  const context = useControlsContext(molstar);
  const onChargeSetSelect = (typeId: number) => {
    context.set.typeId(typeId);
  };

  return (
    <div className="">
      <h3 className="font-bold mb-2">Charge Set</h3>
      <Select
        onValueChange={(value) => onChargeSetSelect(Number(value))}
        defaultValue="1"
      >
        <SelectTrigger className="min-w-[180px] border-2">
          <SelectValue placeholder="Charge Set" />
        </SelectTrigger>
        <SelectContent>
          {molstar &&
            molstar.charges.getMethodNames().map((method, index) => (
              <SelectItem key={index} value={`${index + 1}`}>
                {method}
              </SelectItem>
            ))}
        </SelectContent>
      </Select>
    </div>
  );
};
