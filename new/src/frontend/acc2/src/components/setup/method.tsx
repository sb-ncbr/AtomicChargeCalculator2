import { HTMLAttributes } from "react";
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
import { Separator } from "../ui/separator";
import { cn } from "@acc2/lib/utils";

export type MethodProps = HTMLAttributes<HTMLElement>;

export const Method = ({ className, ...props }: MethodProps) => {
  return (
    <Card {...props} className={cn("rounded-none p-4 mt-4", className)}>
      <h3 className="capitalize font-bold text-xl mb-2">Method</h3>
      <Select>
        <SelectTrigger className="w-[180px] border-2 mb-4">
          <SelectValue placeholder="Method" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>3D</SelectLabel>
            <SelectItem value="sqe+qp">SQE+qp</SelectItem>
            <SelectItem value="eem">EEM</SelectItem>
            <SelectItem value="qeq">QEq</SelectItem>
            <SelectItem value="eqeq">EQeq</SelectItem>
            <SelectItem value="sqe">SQE</SelectItem>
            <SelectItem value="sqe+q0">SQE+q0</SelectItem>
          </SelectGroup>
          <SelectGroup>
            <SelectLabel>2D</SelectLabel>
            <SelectItem value="peoe">PEOE</SelectItem>
            <SelectItem value="dark">MGC</SelectItem>
            <SelectItem value="denr">DENR</SelectItem>
            <SelectItem value="tsef">TSEF</SelectItem>
            <SelectItem value="charge2">Charge2</SelectItem>
            <SelectItem value="veem">VEEM</SelectItem>
          </SelectGroup>
          <SelectGroup>
            <SelectItem value="formal">Formal charges (from file)</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
      <Separator className="my-4" />
      <h4 className="text-sm font-bold">Full Name</h4>
      <p className="text-sm mb-2">
        Split-charge equilibration with parametrized initial charges
      </p>
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
