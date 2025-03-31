import { cn, formatBytes } from "@acc2/lib/utils";
import { Progress } from "../ui/progress";
import { QuotaResponse } from "@acc2/api/files/types";

export type QuotaProgressProps = {
  quota: QuotaResponse;
};

export const QuotaProgress = ({ quota: data }: QuotaProgressProps) => {
  const { usedSpace, quota } = data;

  return (
    <>
      <Progress
        value={(usedSpace / quota) * 100}
        className={"my-4"}
        indicatorClassName={cn(
          usedSpace / quota > 0.5 && "bg-yellow-500",
          usedSpace / quota > 0.8 && "bg-red-500"
        )}
      />
      <span className="font-bold text-sm whitespace-nowrap">
        {formatBytes(usedSpace)} / {formatBytes(quota)}
      </span>
    </>
  );
};
