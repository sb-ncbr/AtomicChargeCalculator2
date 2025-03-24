import { X } from "lucide-react";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";
import { HTMLAttributes } from "react";
import { cn } from "@acc2/lib/utils";
import { useFormContext } from "react-hook-form";
import { SetupFormType } from "@acc2/components/setup/setup";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "../ui/hover-card";

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
      <h3 className="capitalize font-bold text-xl mb-2">Calculations</h3>
      <div className="flex gap-4 flex-wrap">
        {!calculations?.length && <span>No calculations chosen yet.</span>}
        {calculations?.map(({ method, parameters, ...settings }, index) => (
          <HoverCard openDelay={200} closeDelay={0} key={`file-${index}`}>
            <HoverCardTrigger asChild>
              <Badge
                key={index}
                className="w-fit flex justify-between rounded cursor-default"
                variant={"secondary"}
              >
                <span>{method.name}</span>
                {parameters && <span>&nbsp;({parameters.name})</span>}
                {Object.values(settings).map((checked, index) => (
                  <div
                    key={`${method.internalName}-${parameters?.internalName}-${index}`}
                    className={cn(
                      "ml-2 w-2 h-2 rounded-full",
                      checked ? "bg-primary" : "bg-gray-400"
                    )}
                  ></div>
                ))}
                <X
                  height={10}
                  width={10}
                  className="cursor-pointer ml-2 hover:scale-125"
                  onClick={() => removeFromCalculaions(index)}
                />
              </Badge>
            </HoverCardTrigger>
            <HoverCardContent>
              <div className="w-fit flex flex-col gap-2">
                <div className="flex flex-col">
                  <span className="font-bold text-sm">Method</span>
                  <span className="text-xs">{method.name}</span>
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-sm">Parameters</span>
                  <span className="text-xs">{parameters?.name ?? "None"}</span>
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-sm">Read HETATM</span>
                  <span className="text-xs">
                    {settings.readHetatm ? "Enabled" : "Disabled"}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-sm">Ignore water</span>
                  <span className="text-xs">
                    {settings.ignoreWater ? "Enabled" : "Disabled"}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-sm">Permissive types</span>
                  <span className="text-xs">
                    {settings.permissiveTypes ? "Enabled" : "Disabled"}
                  </span>
                </div>
              </div>
            </HoverCardContent>
          </HoverCard>
        ))}
      </div>
    </Card>
  );
};
