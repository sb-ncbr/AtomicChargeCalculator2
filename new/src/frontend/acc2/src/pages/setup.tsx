import { Calculations } from "@acc2/components/setup/calculations";
import { Method } from "@acc2/components/setup/method";
import { Parameters } from "@acc2/components/setup/parameters";
import { Busy } from "@acc2/components/ui/busy";
import { Button } from "@acc2/components/ui/button";
import { Card } from "@acc2/components/ui/card";
import { Form } from "@acc2/components/ui/form";
import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { Separator } from "@acc2/components/ui/separator";
import { useComputationMutation } from "@acc2/hooks/mutations/use-computation-mutation";
import { useTitle } from "@acc2/hooks/use-title";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useSearchParams } from "react-router";
import { toast } from "sonner";
import { z } from "zod";

const setupSchema = z.object({
  method: z.string().nonempty("Method is required."),
  parameters: z.string().optional(),
  computations: z.array(
    z.object({
      method: z.string(),
      parameters: z.string().optional(),
    })
  ),
});

export type SetupFormType = z.infer<typeof setupSchema>;

export const Setup = () => {
  useTitle("Setup");

  const navigate = useNavigate();
  const [searchParams, _] = useSearchParams();
  const computationMutation = useComputationMutation();
  const form = useForm<SetupFormType>({
    resolver: zodResolver(setupSchema),
    defaultValues: {
      method: "",
      parameters: "",
      computations: [],
    },
  });
  const watchForm = form.watch();

  const computationId = searchParams.get("comp_id");
  if (!computationId) {
    navigate("/");
    return null;
  }

  const onSubmit = async (data: SetupFormType) => {
    await computationMutation.mutateAsync(
      {
        computationId,
        computations: data.computations,
      },
      {
        onError: (error) => {
          toast.error(error.message);
        },
        onSuccess: () => {
          navigate({
            pathname: "/results",
            search: `?comp_id=${computationId}`,
          });
        },
      }
    );
  };

  useEffect(() => {
    console.log("watch", watchForm);
  }, [watchForm]);

  return (
    <main className="mx-auto w-full selection:text-white selection:bg-primary mb-12">
      <Busy isBusy={computationMutation.isPending} />
      <ScrollArea type="auto" className="h-full">
        <Card className="w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mt-12 flex flex-col">
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
                <Method computationId={computationId} />
                <Parameters method={watchForm.method} />
              </div>
              <Button
                type="button"
                className="mt-4 self-start"
                variant={"secondary"}
                onClick={() =>
                  form.setValue("computations", [
                    ...form.getValues("computations"),
                    {
                      method: watchForm.method,
                      parameters: watchForm.parameters,
                    },
                  ])
                }
              >
                Add To Calculation
              </Button>
              <Separator className="my-4" />
              <Calculations calculations={watchForm.computations} />
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
