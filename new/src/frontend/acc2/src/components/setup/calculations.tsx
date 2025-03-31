import { X } from "lucide-react";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";
import { HTMLAttributes } from "react";
import { cn } from "@acc2/lib/utils";
import { useFormContext } from "react-hook-form";
import { SetupFormType } from "@acc2/components/setup/setup";
import { InfoTooltip } from "./info-tooltip";
import { HoverDetailsList } from "../shared/hover-details";

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
        {calculations?.map(({ method, parameters, ...settings }, index) => (
          <HoverDetailsList
            trigger={
              <Badge
                key={index}
                className="w-fit flex justify-between rounded cursor-default"
                variant={"secondary"}
              >
                <span>{method.name}</span>
                {parameters && <span>&nbsp;({parameters.name})</span>}
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
              Parameters: parameters?.name ?? "None",
              "Read HETATM": settings.readHetatm ? "Enabled" : "Disabled",
              "Ignore water": settings.ignoreWater ? "Enabled" : "Disabled",
              "Permissive types": settings.permissiveTypes
                ? "Enabled"
                : "Disabled",
            }}
          />
        ))}
      </div>
    </Card>
  );
};
