import type { Method as MethodType } from "@acc2/api/methods/types";
import type { Parameters as ParametersType } from "@acc2/api/parameters/types";

import { handleApiError } from "@acc2/api/base";
import { Calculations } from "@acc2/components/setup/calculations";
import { Method } from "@acc2/components/setup/method/method";
import { Parameters } from "@acc2/components/setup/parameters/parameters";
import { Busy } from "@acc2/components/shared/busy";
import { Button } from "@acc2/components/ui/button";
import { Card } from "@acc2/components/ui/card";
import { Form } from "@acc2/components/ui/form";
import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { Separator } from "@acc2/components/ui/separator";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import { useSuitableMethodsQuery } from "@acc2/lib/hooks/queries/use-calculations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import { z } from "zod";

const setupSchema = z.object({
  computations: z.array(
    z.object({
      method: z.custom<MethodType>(),
      parameters: z.custom<ParametersType>().optional(),
    })
  ),
});

export type SetupFormType = z.infer<typeof setupSchema>;

export type SetupProps = {
  computationId: string;
};

export const Setup = ({ computationId }: SetupProps) => {
  const navigate = useNavigate();

  const {
    data: suitableMethods,
    isPending,
    isError,
  } = useSuitableMethodsQuery(computationId);
  const { computeMutation } = useComputationMutations();

  const [currentMethod, setCurrentMethod] = useState<MethodType | undefined>(
    suitableMethods?.methods?.[0]
  );
  const [currentParameters, setCurrentParameters] = useState<ParametersType>();

  const form = useForm<SetupFormType>({
    resolver: zodResolver(setupSchema),
    defaultValues: {
      computations: [],
    },
  });

  const onSubmit = async (data: SetupFormType) => {
    await computeMutation.mutateAsync(
      {
        computationId,
        fileHashes: [],
        configs: data.computations.map(({ method, parameters }) => ({
          method: method.internalName,
          parameters: parameters?.internalName,
        })),
      },
      {
        onError: (error) => toast.error(handleApiError(error)),
        onSuccess: () => {
          void navigate({
            pathname: "/results",
            search: `?comp_id=${computationId}`,
          });
        },
      }
    );
  };

  const onAddToCalculation = () => {
    if (!currentMethod) {
      return;
    }
    if (currentMethod.hasParameters && !currentParameters) {
      return;
    }

    const computations = form.getValues("computations");
    if (
      computations.find(
        ({ method, parameters }) =>
          method.internalName === currentMethod.internalName &&
          parameters?.internalName === currentParameters?.internalName
      )
    ) {
      return;
    }

    form.setValue("computations", [
      ...form.getValues("computations"),
      {
        method: currentMethod,
        parameters: currentParameters,
      },
    ]);
  };

  const onMethodChange = (method: string) => {
    if (suitableMethods) {
      setCurrentMethod(() =>
        suitableMethods.methods.find((m) => m.internalName === method)
      );
      setCurrentParameters(() => suitableMethods.parameters[method]?.[0]);
    }
  };

  useEffect(() => {
    const defaultMethod = suitableMethods?.methods[0];
    if (suitableMethods && defaultMethod?.hasParameters) {
      setCurrentParameters(
        () => suitableMethods.parameters[defaultMethod.internalName]?.[0]
      );
    }
    setCurrentMethod(() => defaultMethod);
  }, [suitableMethods]);

  useEffect(() => {
    if (isError) {
      void navigate("/");
      toast.error("Something went wrong while fetching setup info.");
    }
  }, [isError]);

  return (
    <main className="mx-auto w-full selection:text-white selection:bg-primary mb-12">
      <ScrollArea type="auto" className="h-full">
        <Card className="w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mt-12 flex flex-col relative">
          <Busy isBusy={computeMutation.isPending || isPending}>
            {computeMutation.isPending && "Computing charges..."}
            {isPending && "Loading suitable methods..."}
          </Busy>
          <h2 className="text-3xl text-primary font-bold mb-2 md:text-5xl">
            Computation Settings
          </h2>
          <p className="text-sm text-foreground/50">
            Note that the list of methods and parameters shows only suitable
            combinations for given input structures. See the complete list of
            parameters.
          </p>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <div className="grid grid-cols-1 xxl:grid-cols-2 gap-4">
                {suitableMethods && (
                  <>
                    <Method
                      currentMethod={currentMethod}
                      suitableMethods={suitableMethods}
                      onMethodChange={onMethodChange}
                    />
                    <Parameters
                      currentParameters={currentParameters}
                      parametersList={
                        suitableMethods.parameters[
                          currentMethod?.internalName ?? ""
                        ] ?? []
                      }
                      onParametersChange={setCurrentParameters}
                    />
                  </>
                )}
              </div>
              <Button
                type="button"
                className="mt-4 self-start"
                variant={"secondary"}
                onClick={onAddToCalculation}
              >
                Add To Calculation
              </Button>
              <Separator className="my-4" />
              <Calculations />
              <div className="self-start mt-4">
                <Button
                  type="submit"
                  className="mr-4"
                  disabled={!form.getValues("computations").length}
                >
                  Compute
                </Button>
                <Button variant={"secondary"} onClick={() => navigate("/")}>
                  Back
                </Button>
              </div>
            </form>
          </Form>
        </Card>
      </ScrollArea>
    </main>
  );
};
