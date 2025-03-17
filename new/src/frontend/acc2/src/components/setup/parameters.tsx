import { Card } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Separator } from "../ui/separator";
import { HTMLAttributes, SetStateAction } from "react";
import { cn } from "@acc2/lib/utils";
import { Parameters as ParametersType } from "@acc2/api/parameters/types";
import { Publication } from "./publication";
import { InfoTooltip } from "./info-tooltip";

type ParametersSelectorProps = {
  currentParameters: ParametersType | undefined;
  parameters: ParametersType[];
  disabled: boolean;
  onParametersChange: React.Dispatch<
    SetStateAction<ParametersType | undefined>
  >;
};

const ParametersSelector = ({
  currentParameters,
  parameters,
  disabled,
  onParametersChange,
}: ParametersSelectorProps) => {
  return (
    <Select
      onValueChange={(value) => {
        if (value) {
          onParametersChange(parameters.find((p) => p.internalName === value));
        }
      }}
      value={currentParameters?.internalName}
      disabled={disabled}
    >
      <SelectTrigger className="w-fit min-w-[220px] max-w-full border-2 mb-4">
        <SelectValue placeholder="Parameters" />
      </SelectTrigger>
      <SelectContent>
        {parameters?.map((parameters, index) => (
          <SelectItem key={index} value={parameters.internalName}>
            {parameters.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

type ParametersPublicationProps = {
  parameters?: ParametersType;
};

const ParametersPublication = ({ parameters }: ParametersPublicationProps) => {
  return <>{parameters && <Publication publicationSource={parameters} />}</>;
};

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
      {/* <Busy isBusy={parametersMutation.isPending} /> */}
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
