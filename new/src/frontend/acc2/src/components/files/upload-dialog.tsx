import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFileUploadMutation } from "@acc2/hooks/mutations/files";
import { handleApiError } from "@acc2/api/base";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { Form } from "../ui/form";
import { Busy } from "../shared/busy";
import { useState } from "react";

const uploadSchema = z.object({
  files: z
    .instanceof(FileList, { message: "Files are required." })
    .refine((files) => files.length > 0),
});

type UploadType = z.infer<typeof uploadSchema>;

export const UploadDialog = () => {
  const queryClient = useQueryClient();
  const uploadMutation = useFileUploadMutation();
  const form = useForm<UploadType>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      files: undefined,
    },
  });
  const [open, setOpen] = useState<boolean>(false);

  const onSubmit = async (data: UploadType) => {
    await uploadMutation.mutateAsync(data.files, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: async () => {
        toast.success("Files have been successfully uploaded.");
        setOpen(false);
        await queryClient.invalidateQueries({
          queryKey: ["files"],
        });
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={(open) => setOpen(open)}>
      <DialogTrigger asChild>
        <div>
          <Button variant={"secondary"}>Upload</Button>
        </div>
      </DialogTrigger>
      <Form {...form}>
        <DialogContent>
          <Busy isBusy={uploadMutation.isPending}></Busy>
          <DialogHeader>
            <DialogTitle>Upload files</DialogTitle>
            <DialogDescription>
              <span className="text-sm text-black text-opacity-40">
                Supported filetypes are <span className="font-bold">sdf</span>,
                <span className="font-bold"> mol2</span>,
                <span className="font-bold"> pdb</span>,
                <span className="font-bold"> mmcif</span>. You can upload one or
                multiple files at the same time. Maximum allowed upload size is
                <span className="font-bold"> 50MB</span>.
              </span>
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <Input
              {...form.register("files")}
              id="files"
              type="file"
              accept=".sdf,.mol2,.pdb,.mmcif,.cif"
              className="border-2 border-primary cursor-pointer"
              multiple
            />
            <DialogFooter className="mt-4">
              <Button variant={"secondary"} onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={!form.formState.isValid}>
                Submit
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Form>
    </Dialog>
  );
};
