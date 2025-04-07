import { Button } from "@acc2/components/ui/button";
import { Input } from "@acc2/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@acc2/components/ui/select";
import { useControlsContext } from "@acc2/lib/hooks/contexts/use-controls-context";
import MolstarPartialCharges from "molstar-partial-charges";
import { HTMLAttributes, useEffect, useRef } from "react";

export const molstarColoringTypes = [
  "structure",
  "charges-relative",
  "charges-absolute",
] as const;

export type MolstarColoringType = (typeof molstarColoringTypes)[number];

export type MolstarColoringControlsProps = {
  molstar: MolstarPartialCharges;
} & HTMLAttributes<HTMLElement>;

export const MolstarColoringControls = ({
  molstar,
}: MolstarColoringControlsProps) => {
  const context = useControlsContext(molstar);
  const maxValueRef = useRef<HTMLInputElement>(null);

  const onMaxValueChange = async (maxValue: number) => {
    context.set.maxValue(maxValue);
  };

  const resetMaxValue = async () => {
    const maxValueInput = maxValueRef?.current;
    if (maxValueInput) {
      const maxCharge = molstar.charges.getMaxCharge();
      maxValueInput.valueAsNumber = maxCharge;
      await onMaxValueChange(maxCharge);
    }
  };

  useEffect(() => {
    if (maxValueRef.current) {
      maxValueRef.current.valueAsNumber = molstar.charges.getMaxCharge();
      maxValueRef.current.max = `${molstar.charges.getMaxCharge()}`;
    }
  }, [molstar]);

  useEffect(() => {
    context.set.coloringType(context.get.coloringType);
    resetMaxValue();
  }, [context.get.coloringType]);

  return (
    <div className="flex gap-4 flex-col sm:flex-row">
      <div className="grow">
        <h3 className="font-bold mb-2">Coloring</h3>
        <Select
          onValueChange={(value) =>
            context.set.coloringType(value as MolstarColoringType)
          }
          defaultValue="charges-relative"
        >
          <SelectTrigger className="min-w-[180px] border-2">
            <SelectValue placeholder="Select Coloring" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem
              value="structure"
              disabled={molstar.type.isDefaultApplicable()}
            >
              Structure
            </SelectItem>
            <SelectItem value="charges-relative">Charges (relative)</SelectItem>
            <SelectItem value="charges-absolute">Charges (absolute)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="w-full col-span-1 sm:w-1/2">
        {context.get.coloringType === "charges-absolute" && (
          <>
            <h3 className="mb-2 w-fit">Max Value</h3>
            <div className="flex gap-4">
              <Input
                ref={maxValueRef}
                type="number"
                className="border-2 lg:min-w-[120px]"
                onChange={({ target }) =>
                  onMaxValueChange(target.valueAsNumber)
                }
                min={0}
                step={0.01}
              />

              <Button
                type="button"
                variant={"secondary"}
                onClick={resetMaxValue}
              >
                Reset
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
