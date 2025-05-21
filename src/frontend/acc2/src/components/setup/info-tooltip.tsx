import { Info } from "lucide-react";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";

export type InfoTooltipProps = {
  info: string;
};

export const InfoTooltip = ({ info }: InfoTooltipProps) => {
  return (
    <TooltipProvider delayDuration={0}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Info className="inline size-5 text-primary cursor-pointer ml-2" />
        </TooltipTrigger>
        <TooltipContent>{info}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
