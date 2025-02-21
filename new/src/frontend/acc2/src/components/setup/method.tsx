import { HTMLAttributes, useEffect, useState } from "react";
import { Card } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Separator } from "../ui/separator";
import { cn } from "@acc2/lib/utils";
import { useSuitableMethodsQuery } from "@acc2/hooks/queries/use-suitable-methods-query";
import { Busy } from "../ui/busy";
import { FormField, FormItem } from "../ui/form";
import { useFormContext } from "react-hook-form";

export type MethodProps = {
  computationId: string;
} & HTMLAttributes<HTMLElement>;

export type MethodSelectorProps = {
  methods: string[];
};

const MethodSelector = ({ methods }: MethodSelectorProps) => {
  const form = useFormContext();

  useEffect(() => {
    form.setValue("method", methods?.[0]);
  }, [methods]);

  return (
    <FormField
      control={form.control}
      name="method"
      render={({ field }) => (
        <FormItem>
          <Select
            {...field}
            onValueChange={field.onChange}
            defaultValue={field.value}
          >
            <SelectTrigger className="w-[180px] border-2 mb-4">
              <SelectValue placeholder="Method" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {methods.map((method, index) => (
                  <SelectItem key={index} value={method}>
                    {method}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </FormItem>
      )}
    ></FormField>
  );
};

const MethodPublication = () => {
  // TODO: change to actual publication
  return (
    <>
      <h4 className="text-sm font-bold">Full Name</h4>
      <p className="text-sm mb-2">
        Split-charge equilibration with parametrized initial charges
      </p>
      <h4 className="text-sm font-bold">Publication</h4>
      <p className="text-sm">
        Schindler, O., Raček, T., Maršavelski, A., Koča, J., Berka, K., &
        Svobodová, R. (2021). Optimized SQE atomic charges for peptides
        accessible via a web application. Journal of cheminformatics, 13(1),
        1-11. doi:10.1186/s13321-021-00528-w
      </p>
    </>
  );
};

export const Method = ({ computationId, className, ...props }: MethodProps) => {
  const { data: suitableMethods, isPending } =
    useSuitableMethodsQuery(computationId);
  const methods = suitableMethods?.success ? suitableMethods.data.methods : [];

  return (
    <Card
      {...props}
      className={cn("rounded-none p-4 mt-4 relative", className)}
    >
      <Busy isBusy={isPending}></Busy>
      <h3 className="capitalize font-bold text-xl mb-2">Method</h3>
      <MethodSelector methods={methods} />
      <Separator className="my-4" />
      <MethodPublication />
    </Card>
  );
};
