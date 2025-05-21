import { Method as MethodType, SuitableMethods } from "@acc2/api/methods/types";
import { cn } from "@acc2/lib/utils";
import { HTMLAttributes } from "react";

import { Card } from "../../ui/card";
import { Separator } from "../../ui/separator";
import { MethodPublication } from "./publication";
import { MethodSelector } from "./selector";

export type MethodProps = {
  suitableMethods: SuitableMethods;
  currentMethod?: MethodType;
  onMethodChange: (method: string) => void;
} & HTMLAttributes<HTMLElement>;

export const Method = ({
  suitableMethods,
  currentMethod,
  onMethodChange,
  className,
  ...props
}: MethodProps) => {
  return (
    <Card {...props} className={cn("rounded-none p-4 mt-4", className)}>
      <h3 className="capitalize font-bold text-xl mb-2">Method</h3>
      <MethodSelector
        methods={suitableMethods?.methods ?? []}
        onMethodChange={onMethodChange}
      />
      <Separator className="my-4" />
      <MethodPublication method={currentMethod} />
    </Card>
  );
};
