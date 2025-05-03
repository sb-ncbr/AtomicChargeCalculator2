import { SetupFormType } from "@acc2/components/setup/setup";
import { cn } from "@acc2/lib/utils";
import { X } from "lucide-react";
import { HTMLAttributes } from "react";
import { useFormContext } from "react-hook-form";

import { HoverDetailsList } from "../shared/hover-details";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";
import { InfoTooltip } from "./info-tooltip";

export type CalculationsProps = HTMLAttributes<HTMLElement>;

export const Calculations = ({ className, ...props }: CalculationsProps) => {
  const form = useFormContext<SetupFormType>();
  const calculations = form.watch("computations");

  const removeFromCalculaions = (index: number) => {
    const computations = form.getValues("computations");
    form.setValue(
      "computations",
      computations.filter((_, i) => i !== index)
    );
  };

  return (
    <Card {...props} className={cn("rounded-none p-4", className)}>
      <h3 className="flex items-center capitalize font-bold text-xl mb-2">
        <span>Calculations</span>
        <InfoTooltip info="Hovering over individual calculations will display its details." />
      </h3>
      <div className="flex gap-4 flex-wrap">
        {!calculations?.length && <span>No calculations chosen yet.</span>}
        {calculations?.map(({ method, parameters }, index) => (
          <HoverDetailsList
            key={`calculation-${index}`}
            trigger={
              <Badge
                key={index}
                className="w-fit flex justify-between rounded cursor-default"
                variant={"secondary"}
              >
                <span>{method.name}</span>
                {parameters && <span>&nbsp;({parameters.fullName})</span>}
                <X
                  height={10}
                  width={10}
                  className="cursor-pointer ml-2 hover:scale-125"
                  onClick={() => removeFromCalculaions(index)}
                />
              </Badge>
            }
            data={{
              Method: method.name,
              Parameters: parameters?.fullName ?? "None",
            }}
          />
        ))}
      </div>
    </Card>
  );
};
