import { BusyContext, BusyContextType } from "@acc2/lib/contexts/busy-context";
import { useContext } from "react";

export type BusyContextHookType = {
  addBusy: () => void;
  removeBusy: () => void;
} & BusyContextType;

export const useBusyContext = (): BusyContextHookType => {
  const context = useContext(BusyContext);

  if (context === null) {
    throw Error("Busy context is null.");
  }

  const addBusy = () => context.setBusyCount((count) => count + 1);

  const removeBusy = () => context.setBusyCount((count) => count - 1);

  return { ...context, addBusy, removeBusy };
};
