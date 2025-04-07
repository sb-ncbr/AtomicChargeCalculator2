import { FileResponse } from "@acc2/api/files/types";
import { HTMLAttributes } from "react";

import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../ui/collapsible";
import { ChevronsUpDown } from "lucide-react";
import { Button } from "../ui/button";
import { cn, downloadBlob, formatBytes } from "@acc2/lib/utils";
import { useFileMutations } from "@acc2/lib/hooks/mutations/use-files";
import { toast } from "sonner";
import { handleApiError } from "@acc2/api/base";
import { useQueryClient } from "@tanstack/react-query";
import { Checkbox } from "../ui/checkbox";
import { CheckedState } from "@radix-ui/react-checkbox";
import { ConfirmAction } from "../shared/confirm-action";

dayjs.extend(localizedFormat);

export type FileProps = {
  file: FileResponse;
  isSelected: boolean;
  onFileSelect: (file: FileResponse, checked: CheckedState) => void;
} & HTMLAttributes<HTMLElement>;

export const File = ({
  file,
  onFileSelect,
  isSelected,
  className,
}: FileProps) => {
  const { fileDeleteMutation, fileDownloadMutation } = useFileMutations();
  const queryClient = useQueryClient();

  const onDelete = async () => {
    await fileDeleteMutation.mutateAsync(file.fileHash, {
      onSuccess: async () => {
        toast.success(`File ${file.fileName} successfully deleted.`);
        await queryClient.invalidateQueries({
          queryKey: ["files"],
        });
      },
      onError: (error) => toast.error(handleApiError(error)),
    });
  };

  const onDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await fileDownloadMutation.mutateAsync(file.fileHash, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: async (data) => downloadBlob(data, file.fileName),
    });
  };

  return (
    <div
      className={cn(
        "w-full border border-solid p-4 relative mb-2 flex flex-col gap-2 hover:bg-secondary/20",
        isSelected ? "bg-secondary/40" : "bg-none",
        className
      )}
      onClick={(e) => {
        e.stopPropagation();
        onFileSelect(file, !isSelected);
      }}
    >
      <Checkbox checked={isSelected} onChange={(e) => e.stopPropagation()} />
      <div className="flex justify-between items-center">
        <span
          className="text-lg font-bold text-primary overflow-ellipsis overflow-hidden w-3/5"
          title={file.fileName}
        >
          {file.fileName}
        </span>
        <div className="min-w-36">
          <span className="block text-end text-xs">
            {dayjs(file.uploadedAt).format("LLL")}
          </span>
          <span className="block text-end text-xs">
            {formatBytes(file.size)}
          </span>
        </div>
      </div>
      <Collapsible>
        <CollapsibleTrigger asChild onClick={(e) => e.stopPropagation()}>
          <div className="flex gap-2 items-center cursor-pointer">
            <span className="font-semibold">Statistics</span>
            <ChevronsUpDown height={15} width={15} />
          </div>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="text-sm pl-4 mt-2 border-l border-gray-200">
            <div className="flex flex-col">
              <span className="mr-2 font-bold">Total Molecules</span>
              <span>{file.stats.totalMolecules}</span>
            </div>
            <div className="flex flex-col text=sm">
              <span className="mr-2 font-bold">Total Atoms</span>
              <span>{file.stats.totalAtoms}</span>
            </div>
            <div className="text-sm">
              <span className="block font-bold">Atom Type Counts</span>
              {file.stats?.atomTypeCounts
                .toSorted((a, b) => a.symbol.localeCompare(b.symbol))
                .map(({ symbol, count }, index) => (
                  <div key={`${file.fileHash}-atomTypeCounts-${index}`}>
                    <span className="font-bold mr-1 text-muted-foreground">
                      {symbol}:
                    </span>
                    <span className="mr-2">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
      <div className="mt-4 flex flex-col justify-end gap-2 xs:flex-row">
        <Button
          type="button"
          variant={"secondary"}
          className="self-end w-full xs:w-28"
          onClick={onDownload}
        >
          Download
        </Button>
        <ConfirmAction
          trigger={
            <Button
              type="button"
              variant={"destructive"}
              className="self-end w-full xs:w-28"
              onClick={(e) => e.stopPropagation()}
            >
              Delete
            </Button>
          }
          onConfirm={onDelete}
          title="Confirmation"
          description={`Are you sure you want to delete "${file.fileName}" file?`}
        />
      </div>
    </div>
  );
};
