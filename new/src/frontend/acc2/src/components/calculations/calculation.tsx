import { HTMLAttributes } from "react";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { cn, downloadBlob } from "@acc2/lib/utils";
import { useNavigate } from "react-router";
import { CalculationPreview } from "@acc2/api/calculations/types";
import { toast } from "sonner";
import { handleApiError } from "@acc2/api/base";

import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "../ui/hover-card";
import { useCalculationDownloadMutation } from "@acc2/hooks/mutations/use-calculation-download-mutation";
import { useCalculationDeleteMutation } from "@acc2/hooks/mutations/calculations";
import { useQueryClient } from "@tanstack/react-query";
import { InfoTooltip } from "../setup/info-tooltip";
import { ConfirmAction } from "../shared/confirm-action";

dayjs.extend(localizedFormat);

export type CalculationProps = {
  calculation: CalculationPreview;
} & HTMLAttributes<HTMLElement>;

export const Calculation = ({
  calculation,
  className,
  ...props
}: CalculationProps) => {
  const { id, configs, files, createdAt } = calculation;
  const navigate = useNavigate();
  const downloadMutation = useCalculationDownloadMutation();
  const deleteMutation = useCalculationDeleteMutation();
  const queryClient = useQueryClient();

  const onDownload = async () => {
    await downloadMutation.mutateAsync(id, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: async (data) => downloadBlob(data, "charges.zip"),
    });
  };

  const onDelete = async () => {
    await deleteMutation.mutateAsync(id, {
      onError: (error) => toast.error(handleApiError(error)),
      onSuccess: async () => {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ["calculations"] }),
          queryClient.invalidateQueries({ queryKey: ["files"] }),
        ]);
        toast.success("Calculation successfully deleted.");
      },
    });
  };

  return (
    <div
      {...props}
      className={cn("w-full border border-solid p-4 relative", className)}
    >
      <div className="mb-4">
        <span className="block font-bold text-md mb-2">
          Files
          <InfoTooltip info="Hovering over the individual files will show their statistics." />
        </span>
        <div className="flex gap-2 flex-wrap">
          {Object.entries(files)
            .toSorted((a, b) => a[0].localeCompare(b[0]))
            .map(([file, stats], index) => (
              <HoverCard openDelay={0} closeDelay={0} key={`file-${index}`}>
                <HoverCardTrigger asChild>
                  <Badge className="cursor-pointer rounded" variant="secondary">
                    {file}
                  </Badge>
                </HoverCardTrigger>
                <HoverCardContent className="bg-white border z-50 p-4 text-sm shadow mt-2 flex flex-col gap-2">
                  <div className="flex flex-col">
                    <span className="mr-2 font-bold">Total Molecules</span>
                    <span>{stats.totalMolecules}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="mr-2 font-bold">Total Atoms</span>
                    <span>{stats.totalAtoms}</span>
                  </div>
                  <div>
                    <span className="block font-bold">Atom Type Counts</span>
                    {stats.atomTypeCounts
                      .toSorted((a, b) => a.symbol.localeCompare(b.symbol))
                      .map(({ symbol, count }, index) => (
                        <div
                          key={`${calculation.id}-${file}-atomTypeCounts-${index}`}
                        >
                          <span className="font-bold mr-1 text-muted-foreground">
                            {symbol}:
                          </span>
                          <span className="mr-2">{count}</span>
                        </div>
                      ))}
                  </div>
                </HoverCardContent>
              </HoverCard>
            ))}
        </div>
      </div>
      <div>
        <span className="block font-bold mb-2">Calculations</span>
        <div className="flex gap-2 flex-wrap">
          {configs.map(({ method, parameters }, index) => (
            <Badge
              key={`molecule-${index}`}
              className="cursor-default rounded"
              variant="secondary"
            >
              <span>{method}</span>
              {parameters && <span>&nbsp;({parameters})</span>}
            </Badge>
          ))}
        </div>
      </div>
      <div className="mt-4 flex flex-col justify-end gap-2 xs:flex-row">
        <Button
          type="button"
          variant={"default"}
          className="self-end w-full xs:w-28"
          onClick={() => {
            navigate({
              pathname: "/results",
              search: `?comp_id=${id}`,
            });
          }}
        >
          View
        </Button>
        <Button
          type="button"
          variant={"secondary"}
          className="self-end w-full xs:w-28"
          onClick={onDownload}
        >
          Download
        </Button>
        <ConfirmAction
          onConfirm={onDelete}
          trigger={
            <Button
              type="button"
              variant={"destructive"}
              className="self-end w-full xs:w-28"
            >
              Delete
            </Button>
          }
          description="Are you sure you want to delete this calculation?"
          title="Confirmation"
        />
      </div>
      <span className="absolute right-4 top-4 text-xs">
        {dayjs(createdAt).format("LLL")}
      </span>
    </div>
  );
};
