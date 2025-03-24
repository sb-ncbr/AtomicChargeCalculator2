import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@acc2/components/ui/select";
import { Parameters } from "@acc2/api/parameters/types";
import { SetStateAction } from "react";

export type ParametersSelectorProps = {
  currentParameters: Parameters | undefined;
  parameters: Parameters[];
  disabled: boolean;
  onParametersChange: React.Dispatch<SetStateAction<Parameters | undefined>>;
};

export const ParametersSelector = ({
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
