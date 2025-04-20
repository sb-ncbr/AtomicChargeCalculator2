import { handleApiError } from "@acc2/api/base";
import { FileResponse } from "@acc2/api/files/types";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import { useState } from "react";
import { createSearchParams, useNavigate } from "react-router";
import { toast } from "sonner";

import { Busy } from "../shared/busy";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";

export type ComputeDialogProps = {
  files: FileResponse[];
};

export const ComputeDialog = ({ files }: ComputeDialogProps) => {
  const [open, setOpen] = useState<boolean>(false);

  const { computeMutation, setupMutation } = useComputationMutations();
  const navigate = useNavigate();

  const onCompute = async () => {
    await computeMutation.mutateAsync(
      {
        fileHashes: files.map((file) => file.fileHash),
        configs: [],
      },
      {
        onError: (error) => toast.error(handleApiError(error)),
        onSuccess: (compId) => {
          void navigate({
            pathname: "/results",
            search: createSearchParams({
              comp_id: compId,
            }).toString(),
          });
        },
      }
    );
  };

  const onSetup = async () => {
    await setupMutation.mutateAsync(
      {
        fileHashes: files.map((file) => file.fileHash),
      },
      {
        onError: (error) => toast.error(handleApiError(error)),
        onSuccess: async (compId) => {
          void navigate({
            pathname: "/setup",
            search: createSearchParams({
              comp_id: compId,
            }).toString(),
          });
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={(open) => setOpen(open)}>
      <DialogTrigger asChild>
        <Button disabled={files.length === 0}>Compute</Button>
      </DialogTrigger>
      <DialogContent>
        <Busy isBusy={computeMutation.isPending} />
        <DialogHeader>
          <DialogTitle>Compute charges.</DialogTitle>
          <DialogDescription>
            <span>Start computation with the selected files.</span>
          </DialogDescription>
        </DialogHeader>
        <div>
          <div>
            <span className="block mr-2 text-sm">Selected files:</span>
            {files.map((file) => (
              <Badge
                key={`selected-dialog-${file.fileHash}`}
                variant={"secondary"}
                className="mr-2 rounded"
              >
                {file.fileName}
              </Badge>
            ))}
          </div>
        </div>
        <DialogFooter className="mt-4">
          <Button variant={"ghost"} onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant={"secondary"} onClick={onSetup}>
            Setup Computation
          </Button>
          <Button onClick={onCompute}>Compute</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
