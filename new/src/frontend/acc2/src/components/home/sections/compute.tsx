import { handleApiError } from "@acc2/api/base";
import { Busy } from "@acc2/components/shared/busy";
import { Button } from "@acc2/components/ui/button";
import { Card } from "@acc2/components/ui/card";
import { Form } from "@acc2/components/ui/form";
import { Input } from "@acc2/components/ui/input";
import { Label } from "@acc2/components/ui/label";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import { useFileMutations } from "@acc2/lib/hooks/mutations/use-files";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { createSearchParams, useNavigate } from "react-router";
import { toast } from "sonner";
import z from "zod";

const computeSchema = z.object({
  files: z
    .instanceof(FileList, { message: "Files are required." })
    .refine((files) => files.length > 0),
});

type ComputeType = z.infer<typeof computeSchema>;

export const Compute = () => {
  const navigate = useNavigate();
  const { fileUploadMutation } = useFileMutations();
  const { computeMutation, setupMutation } = useComputationMutations();

  const form = useForm<ComputeType>({
    resolver: zodResolver(computeSchema),
    defaultValues: {
      files: undefined,
    },
  });

  const onSubmit = async (data: ComputeType) => {
    await fileUploadMutation.mutateAsync(data.files, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: async (uploadResponse) => {
        await computeMutation.mutateAsync(
          {
            fileHashes: uploadResponse.map((file) => file.fileHash),
            configs: [],
          },
          {
            onError: (error) => toast.error(handleApiError(error)),
            onSuccess: (compId) => {
              void navigate({
                pathname: "results",
                search: createSearchParams({
                  comp_id: compId,
                }).toString(),
              });
            },
          }
        );
      },
    });
  };

  const onSetup = async (data: ComputeType) => {
    await fileUploadMutation.mutateAsync(data.files, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: async (uploadResponse) => {
        await setupMutation.mutateAsync(
          uploadResponse.map((file) => file.fileHash),
          {
            onError: () =>
              toast.error("Unable to setup computation. Try again later."),
            onSuccess: (compId) => {
              void navigate({
                pathname: "setup",
                search: createSearchParams({
                  comp_id: compId,
                }).toString(),
              });
            },
          }
        );
      },
    });
  };

  return (
    <Card className="w-11/12 md:w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mb-12 mt-0 xs:mt-8 md:mt-0 relative">
      <Busy
        isBusy={computeMutation.isPending || fileUploadMutation.isPending}
      />
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
            <Button
              type="submit"
              title="Direct computation of charges using automatically selected empirical charge calculation method."
              disabled={!form.formState.isValid}
            >
              Compute
            </Button>
            <Button
              type="button"
              title="Selection of empirical charge calculation method and its parameters."
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
