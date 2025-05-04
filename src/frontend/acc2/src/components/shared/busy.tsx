import { cn } from "@acc2/lib/utils";
import { LoaderCircle } from "lucide-react";
import { HTMLAttributes, PropsWithChildren, useEffect, useState } from "react";
import { useDebouncedCallback } from "use-debounce";

export type BusyProps = {
  isBusy: boolean;
  size?: BusySize;
  fullscreen?: boolean;
} & HTMLAttributes<HTMLElement> &
  PropsWithChildren;

export enum BusySize {
  Big = 50,
  Small = 25,
}

// We don't want to show busy if loading takes short amount of time to avoid flickering.
const BusyDelayMs = 200;

export const Busy = ({
  isBusy,
  size = BusySize.Small,
  fullscreen = false,
  children,
  className,
  ...rest
}: BusyProps) => {
  const [showBusy, setShowBusy] = useState<boolean>(false);

  const triggerBusy = useDebouncedCallback(() => {
    setShowBusy(true);
  }, BusyDelayMs);

  useEffect(() => {
    if (isBusy) {
      triggerBusy();
    } else {
      triggerBusy.cancel();
      setShowBusy(false);
    }
  }, [isBusy]);

  return (
    <div
      {...rest}
      className={cn(
        "inset-0 bg-secondary/35 place-content-center z-40",
        fullscreen ? "fixed" : "absolute",
        showBusy ? "grid" : "hidden",
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
