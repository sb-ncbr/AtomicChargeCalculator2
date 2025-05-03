import { Method as MethodType } from "@acc2/api/methods/types";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@acc2/components/ui/select";

export type MethodSelectorProps = {
  methods: MethodType[];
  onMethodChange: (method: string) => void;
};

export const MethodSelector = ({
  methods,
  onMethodChange,
}: MethodSelectorProps) => {
  return (
    <Select
      onValueChange={onMethodChange}
      defaultValue={methods?.[0].internalName}
    >
      <SelectTrigger className="w-fit min-w-[220px] max-w-full border-2 mb-4">
        <SelectValue placeholder="Method" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          {Object.entries(Object.groupBy(methods, ({ type }) => type)).map(
            ([type, methods]) => (
              <SelectGroup key={type}>
                <SelectLabel>{type}</SelectLabel>
                {methods.map((method, index) => (
                  <SelectItem key={index} value={method.internalName}>
                    {method.name}
                  </SelectItem>
                ))}
              </SelectGroup>
            )
          )}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
};
