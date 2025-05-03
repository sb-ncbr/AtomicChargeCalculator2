import { MolstarColoringType } from "@acc2/components/results/controls/coloring-controls";
import { MolstarViewType } from "@acc2/components/results/controls/view-controls";
import React, { createContext } from "react";

export type ControlsState = {
  currentTypeId: number;
  structure: string;
  coloring: {
    type: MolstarColoringType;
    maxValue: number;
  };
  view: MolstarViewType;
};

export type ControlsContextType = {
  currentTypeId: number;
  setCurrentTypeId: React.Dispatch<React.SetStateAction<number>>;
  structure: string;
  setStructure: React.Dispatch<React.SetStateAction<string>>;
  coloringType: MolstarColoringType;
  setColoringType: React.Dispatch<React.SetStateAction<MolstarColoringType>>;
  maxValue: number;
  setMaxValue: React.Dispatch<React.SetStateAction<number>>;
  viewType: MolstarViewType;
  setViewType: React.Dispatch<React.SetStateAction<MolstarViewType>>;
  methodNames: (string | undefined)[];
  setMethodNames: React.Dispatch<React.SetStateAction<(string | undefined)[]>>;
};

export const ControlsContext = createContext<ControlsContextType | null>(null);

export const ControlsContextProvider = ControlsContext.Provider;
