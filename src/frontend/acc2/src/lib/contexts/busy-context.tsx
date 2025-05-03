import { createContext } from "react";

export type BusyContextType = {
  busyCount: number;
  setBusyCount: React.Dispatch<React.SetStateAction<number>>;
};

export const BusyContext = createContext<BusyContextType | null>(null);

export const BusyContextProvider = BusyContext.Provider;
