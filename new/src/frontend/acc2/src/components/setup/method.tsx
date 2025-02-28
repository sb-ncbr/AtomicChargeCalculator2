import { HTMLAttributes } from "react";
import { Card } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Separator } from "../ui/separator";
import { cn } from "@acc2/lib/utils";
import { Method as MethodType, SuitableMethods } from "@acc2/api/methods/types";
import { usePublicationQuery } from "@acc2/hooks/queries/use-publication-query";

export type MethodSelectorProps = {
  methods: MethodType[];
  onMethodChange: (method: string) => void;
};

const MethodSelector = ({ methods, onMethodChange }: MethodSelectorProps) => {
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

type MethodPublicationProps = {
  method?: MethodType;
};

const MethodPublication = ({ method }: MethodPublicationProps) => {
  const { data: publication } = usePublicationQuery(method);

  return (
    <>
      <h4 className="text-sm font-bold">Full Name</h4>
      <p className="text-sm mb-2">{method?.fullName}</p>
      {publication && (
        <>
          <h4 className="text-sm font-bold">Publication</h4>
          <p className="text-sm">{publication}</p>
        </>
      )}
    </>
  );
};

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
