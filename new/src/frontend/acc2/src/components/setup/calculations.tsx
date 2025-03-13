import { X } from "lucide-react";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";
import { HTMLAttributes } from "react";
import { cn } from "@acc2/lib/utils";
import { useFormContext } from "react-hook-form";
import { SetupFormType } from "@acc2/components/setup/setup";

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
        {calculations?.map(({ method, parameters }, index) => (
          <Badge
            key={index}
            className="w-fit flex justify-between rounded"
            variant={"secondary"}
          >
            <span>{method.name}</span>
            {parameters && <span>&nbsp;({parameters.name})</span>}
            <X
              height={10}
              width={10}
              className="cursor-pointer ml-2"
              onClick={() => removeFromCalculaions(index)}
            />
          </Badge>
        ))}
      </div>
    </Card>
  );
};
