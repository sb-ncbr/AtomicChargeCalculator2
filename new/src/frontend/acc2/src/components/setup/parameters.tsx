import { Info } from "lucide-react";
import { Card } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import { Separator } from "../ui/separator";
import { HTMLAttributes } from "react";
import { cn } from "@acc2/lib/utils";

export type ParametersProps = HTMLAttributes<HTMLElement>;

export const Parameters = ({ className, ...props }: ParametersProps) => {
  return (
    <Card {...props} className={cn("rounded-none p-4 mt-4", className)}>
      <h3 className="capitalize font-bold text-xl mb-2">
        Parameters
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info className="inline size-5 text-primary cursor-pointer ml-2" />
            </TooltipTrigger>
            <TooltipContent>
              The most suitable parameters are shown first.
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </h3>
      <Select>
        <SelectTrigger className="w-[180px] border-2 mb-4">
          <SelectValue placeholder="Parameters" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>2D</SelectLabel>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">System</SelectItem>
          </SelectGroup>
          <SelectGroup>
            <SelectLabel>3D</SelectLabel>
            <SelectItem value="light3d">Light</SelectItem>
            <SelectItem value="dark3d">Dark</SelectItem>
            <SelectItem value="system3d">System</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
      <Separator className="my-4" />
      <h4 className="text-sm font-bold">Publication</h4>
      <p className="text-sm">
        Schindler, O., Raček, T., Maršavelski, A., Koča, J., Berka, K., &
        Svobodová, R. (2021). Optimized SQE atomic charges for peptides
        accessible via a web application. Journal of cheminformatics, 13(1),
        1-11. doi:10.1186/s13321-021-00528-w
      </p>
    </Card>
  );
};
