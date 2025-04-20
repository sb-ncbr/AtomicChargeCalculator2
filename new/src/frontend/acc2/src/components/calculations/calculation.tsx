import { handleApiError } from "@acc2/api/base";
import { CalculationPreview } from "@acc2/api/calculations/types";
import { useComputationMutations } from "@acc2/lib/hooks/mutations/use-calculations";
import { cn, downloadBlob } from "@acc2/lib/utils";
import { useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import { HTMLAttributes } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

import { InfoTooltip } from "../setup/info-tooltip";
import { ConfirmAction } from "../shared/confirm-action";
import { HoverDetailsList } from "../shared/hover-details";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "../ui/hover-card";

dayjs.extend(localizedFormat);

export type CalculationProps = {
  calculation: CalculationPreview;
} & HTMLAttributes<HTMLElement>;

export const Calculation = ({
  calculation,
  className,
  ...props
}: CalculationProps) => {
  const { id, configs, files, settings, createdAt } = calculation;

  const navigate = useNavigate();
  const { downloadMutation, deleteMutation } = useComputationMutations();
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
          <InfoTooltip info="Hovering over individual files will show their statistics." />
        </span>
        <div className="flex gap-2 flex-wrap">
          {Object.entries(files)
            .toSorted((a, b) => a[0].localeCompare(b[0]))
            .map(([file, stats], index) => (
              <HoverCard openDelay={0} closeDelay={0} key={`file-${index}`}>
                <HoverCardTrigger>
                  <Badge className="cursor-pointer rounded" variant="secondary">
                    {file}
                  </Badge>
                </HoverCardTrigger>
                <HoverCardContent className="bg-white border z-50 p-4 text-sm shadow mt-2 flex flex-col gap-2">
                  <div className="flex flex-col">
                    <span className="mr-2 font-bold">Total Molecules</span>
                    <span className="text-xs">{stats.totalMolecules}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="mr-2 font-bold">Total Atoms</span>
                    <span className="text-xs">{stats.totalAtoms}</span>
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
                          <span className="mr-2 text-xs">{count}</span>
                        </div>
                      ))}
                  </div>
                </HoverCardContent>
              </HoverCard>
            ))}
        </div>
      </div>
      <div className="mb-4">
        <span className="block font-bold text-md mb-2">
          Calculations
          <InfoTooltip info="Hovering over individual calculations will display its details." />
        </span>
        <div className="flex gap-2 flex-wrap">
          {configs.map(({ method, parameters }, index) => (
            <HoverDetailsList
              key={`${calculation.id}-molecule-${index}`}
              trigger={
                <Badge className="cursor-pointer rounded" variant="secondary">
                  <span>{method}</span>
                  {parameters && <span>&nbsp;({parameters})</span>}
                </Badge>
              }
              data={{
                Method: method,
                Parameters: parameters ?? "None",
              }}
            />
          ))}
        </div>
      </div>
      {Object.values(settings).some(Boolean) && (
        <div>
          <span className="block font-bold text-md mb-2">
            Advanced Settings
          </span>
          <div className="flex gap-2 flex-wrap">
            {settings.readHetatm && (
              <Badge className="rounded" variant={"secondary"}>
                Read HETATM
              </Badge>
            )}
            {settings.ignoreWater && (
              <Badge className="rounded" variant={"secondary"}>
                Ignore water
              </Badge>
            )}
            {settings.permissiveTypes && (
              <Badge className="rounded" variant={"secondary"}>
                Permissive types
              </Badge>
            )}
          </div>
        </div>
      )}
      <div className="mt-4 flex flex-col justify-end gap-2 xs:flex-row">
        <Button
          type="button"
          variant={"default"}
          className="self-end w-full xs:w-28"
          onClick={() => {
            void navigate({
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
