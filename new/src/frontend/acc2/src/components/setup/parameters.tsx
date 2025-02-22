import { Info } from "lucide-react";
import { Card } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import { Separator } from "../ui/separator";
import { HTMLAttributes, useEffect, useState } from "react";
import { cn } from "@acc2/lib/utils";
import { useAvailableParametersMutation } from "@acc2/hooks/mutations/use-available-parameters-mutation";
import { Busy } from "../ui/busy";
import { useFormContext } from "react-hook-form";
import { FormField, FormItem } from "../ui/form";
import { SetupFormType } from "@acc2/pages/setup";
import { toast } from "sonner";
import { handleApiError } from "@acc2/api/base";

type ParametersSelectorProps = {
  parameters: string[];
};

const ParametersSelector = ({ parameters }: ParametersSelectorProps) => {
  const form = useFormContext<SetupFormType>();

  useEffect(() => {
    form.setValue("parameters", parameters?.[0]);
  }, [parameters]);

  return (
    <FormField
      control={form.control}
      name="parameters"
      render={({ field }) => (
        <FormItem>
          <Select
            {...field}
            onValueChange={field.onChange}
            disabled={parameters.length === 0}
          >
            <SelectTrigger className="w-[180px] border-2 mb-4">
              <SelectValue placeholder="Parameters" />
            </SelectTrigger>
            <SelectContent>
              {parameters.map((parameters, index) => (
                <SelectItem key={index} value={parameters}>
                  {parameters}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FormItem>
      )}
    ></FormField>
  );
};

const ParametersPublication = () => {
  return (
    <>
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

export type ParametersProps = HTMLAttributes<HTMLElement>;

export const Parameters = ({ className, ...props }: ParametersProps) => {
  const form = useFormContext<SetupFormType>();
  const method = form.watch("method");
  const parametersMutation = useAvailableParametersMutation();
  const [parameters, setParameters] = useState<string[]>([]);

  const getParameters = async () => {
    if (!method) {
      return;
    }

    await parametersMutation.mutateAsync(method, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: (parameters) => setParameters(parameters),
    });
  };

  useEffect(() => {
    getParameters();
  }, [method]);

  return (
    <Card
      {...props}
      className={cn("rounded-none p-4 mt-4 relative", className)}
    >
      <Busy isBusy={parametersMutation.isPending} />
      <h3 className="capitalize font-bold text-xl mb-2">
        Parameters
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info className="inline size-5 text-primary cursor-pointer ml-2" />
            </TooltipTrigger>
            <TooltipContent>
              The most suitable parameters are shown first.
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </h3>
      <ParametersSelector parameters={parameters} />
      <Separator className="my-4" />
      <ParametersPublication />
    </Card>
  );
};
