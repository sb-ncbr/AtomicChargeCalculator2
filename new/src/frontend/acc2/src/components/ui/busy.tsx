import { cn } from "@acc2/lib/utils";
import { LoaderCircle } from "lucide-react";
import { HTMLAttributes, PropsWithChildren } from "react";

export type BusyProps = {
  isBusy: boolean;
  size?: BusySize;
} & HTMLAttributes<HTMLElement> &
  PropsWithChildren;

export enum BusySize {
  Big = 50,
  Small = 25,
}

export const Busy = ({
  isBusy,
  size = BusySize.Small,
  children,
  className,
  ...rest
}: BusyProps) => {
  return (
    <div
      {...rest}
      className={cn(
        "absolute inset-0 bg-secondary/35 place-content-center z-40",
        isBusy ? "grid" : "hidden",
        className
      )}
    >
      <span className="flex gap-4 items-center text-primary">
        <LoaderCircle size={size} className="animate-spin" />
        {children}
      </span>
    </div>
  );
};
