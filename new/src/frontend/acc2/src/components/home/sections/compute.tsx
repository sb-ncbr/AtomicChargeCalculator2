import { Button } from "@acc2/components/ui/button";
import { Card } from "@acc2/components/ui/card";
import { Input } from "@acc2/components/ui/input";
import { Label } from "@acc2/components/ui/label";
import { createSearchParams, useNavigate } from "react-router";
import { useForm } from "react-hook-form";
import { Form } from "@acc2/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import z from "zod";
import { useComputationSetupMutation } from "@acc2/hooks/mutations/use-computation-setup-mutation";
import { toast } from "sonner";
import { useComputationMutation } from "@acc2/hooks/mutations/use-computation-mutation";
import { Busy } from "@acc2/components/ui/busy";

const computeSchema = z.object({
  files: z
    .instanceof(FileList, { message: "Files are required." })
    .refine((files) => files.length > 0),
});

type ComputeType = z.infer<typeof computeSchema>;

export const Compute = () => {
  const navigate = useNavigate();
  const setupMutation = useComputationSetupMutation();
  const computationMutation = useComputationMutation();

  const form = useForm<ComputeType>({
    resolver: zodResolver(computeSchema),
    defaultValues: {
      files: undefined,
    },
  });

  const onSubmit = async (data: ComputeType) => {
    const setupResponse = await setupMutation.mutateAsync(data.files);

    if (!setupResponse.success) {
      console.log(setupResponse.message);
      return;
    }

    await computationMutation.mutateAsync(
      {
        computationId: setupResponse.data.computationId,
      },
      {
        onError: (error) => toast.error(error.message),
      }
    );

    navigate({
      pathname: "results",
      search: createSearchParams({
        comp_id: setupResponse.data.computationId,
      }).toString(),
    });
  };

  const onSetup = async (data: ComputeType) => {
    const response = await setupMutation.mutateAsync(data.files, {
      onError: () => toast.error("Unable to upload file(s). Try again later."),
    });

    if (!response.success) {
      console.error(response.message);
      return;
    }

    navigate({
      pathname: "setup",
      search: createSearchParams({
        comp_id: response.data.computationId,
      }).toString(),
    });
  };

  return (
    <Card className="w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mb-12 mt-0 xs:mt-8 md:mt-0 relative">
      {/* {setupMutation.isPending && (
        <div className="absolute inset-0">
          <Progress value={25} className="rounded-none" />
        </div>
      )} */}
      <Busy isBusy={computationMutation.isPending} />
      <h2 className="text-5xl text-primary font-bold">Compute</h2>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <div className="my-4 flex flex-col gap-2">
            <Label className="font-bold text-lg">Upload structures</Label>
            <Input
              {...form.register("files")}
              id="files"
              type="file"
              accept=".sdf,.mol2,.pdb,.mmcif,.cif"
              className="border-2 border-primary cursor-pointer xs:w-fit"
              multiple
            />
            <p className="text-sm text-black text-opacity-40">
              Supported filetypes are <span className="font-bold">sdf</span>,
              <span className="font-bold"> mol2</span>,
              <span className="font-bold"> pdb</span>,
              <span className="font-bold"> mmcif</span>. You can upload one or
              multiple files at the same time. Maximum allowed upload size is
              <span className="font-bold"> 250MB</span>.
            </p>
          </div>
          <div className="flex gap-4 flex-col xs:flex-row">
            <Button type="submit" disabled={!form.formState.isValid}>
              Compute
            </Button>
            <Button
              type="button"
              variant={"secondary"}
              disabled={!form.formState.isValid}
              onClick={() => onSetup(form.getValues())}
            >
              Setup Computation
            </Button>
          </div>
        </form>
      </Form>
    </Card>
  );
};
