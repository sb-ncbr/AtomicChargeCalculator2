import { Card } from "../../ui/card";
import { Separator } from "../../ui/separator";
import { HTMLAttributes } from "react";
import { cn } from "@acc2/lib/utils";
import { Parameters as ParametersType } from "@acc2/api/parameters/types";
import { InfoTooltip } from "../info-tooltip";
import { ParametersPublication } from "./publication";
import { ParametersSelector } from "./selector";

export type ParametersProps = {
  currentParameters: ParametersType | undefined;
  parametersList: ParametersType[];
  onParametersChange: React.Dispatch<
    React.SetStateAction<ParametersType | undefined>
  >;
} & HTMLAttributes<HTMLElement>;

export const Parameters = ({
  currentParameters,
  parametersList,
  onParametersChange,
  className,
  ...props
}: ParametersProps) => {
  return (
    <Card
      {...props}
      className={cn("rounded-none p-4 mt-4 relative", className)}
    >
      <h3 className="capitalize font-bold text-xl mb-2">
        Parameters
        <InfoTooltip info="The most suitable parameters are shown first." />
      </h3>
      <ParametersSelector
        currentParameters={currentParameters}
        disabled={parametersList.length === 0}
        parameters={parametersList}
        onParametersChange={onParametersChange}
      />
      <Separator className="my-4" />
      <ParametersPublication parameters={currentParameters} />
    </Card>
  );
};
