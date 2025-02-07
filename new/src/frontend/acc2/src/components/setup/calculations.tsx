import { X } from "lucide-react";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";
import { HTMLAttributes } from "react";
import { cn } from "@acc2/lib/utils";

export type CalculationsProps = HTMLAttributes<HTMLElement>;

export const Calculations = ({ className, ...props }: CalculationsProps) => {
  const calculations: { method: string; parameters: string }[] = [
    { method: "eem", parameters: "EEM_00_NEEMP_ccd2016_npa" },
    { method: "veem", parameters: "" },
    { method: "eqeq", parameters: "" },
    { method: "sqeq0", parameters: "SQEq0_00_Schindler2021_PUB_pept" },
  ];

  return (
    <Card {...props} className={cn("rounded-none p-4", className)}>
      <h3 className="capitalize font-bold text-xl mb-2">Calculations</h3>
      <div className="flex gap-4 flex-wrap">
        {calculations.map(({ method, parameters }, index) => (
          <Badge
            key={index}
            className="w-fit flex justify-between rounded-sm"
            variant={"secondary"}
          >
            <span>{method}</span>
            {parameters && <span>&nbsp;({parameters})</span>}
            <X height={10} width={10} className="cursor-pointer ml-2" />
          </Badge>
        ))}
      </div>
    </Card>
  );
};
