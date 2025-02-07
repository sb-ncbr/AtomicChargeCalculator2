import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Input } from "../ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Separator } from "../ui/separator";

export const Controls = () => {
  return (
    <Card className="w-4/5 rounded-none mx-auto p-4 max-w-content mt-4 flex flex-col">
      <div className="flex gap-2">
        <h3 className="font-bold">Method:</h3>
        <span>SQE+qp</span>
      </div>
      <div className="flex gap-2">
        <h3 className="font-bold">Parameters:</h3>
        <span>Schindler 2021 (CCD_gen)</span>
      </div>
      <Separator className="my-4" />
      <div className="grid grid-cols-1 lg:grid-cols-2 xxl:grid-cols-3 gap-4">
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          <div>
            <h3 className="font-bold mb-2">Structure</h3>
            <Select>
              <SelectTrigger className="min-w-[180px] border-2">
                <SelectValue placeholder="Structure" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="propofol">PROPOFOL</SelectItem>
                <SelectItem value="o_cresol">O_CRESOL</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="">
            <h3 className="font-bold mb-2">Charge Set</h3>
            <Select>
              <SelectTrigger className="min-w-[180px] border-2">
                <SelectValue placeholder="Charge Set" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sqe+qp/Schindler 2021 (CCD_gen)">
                  SQE+qp/Schindler 2021 (CCD_gen)
                </SelectItem>
                <SelectItem value="idk">idk</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div>
          <div>
            <h3 className="font-bold mb-2">View</h3>
            <Select>
              <SelectTrigger className="md:min-w-[180px] border-2">
                <SelectValue placeholder="Select View" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cartoon">Cartoon</SelectItem>
                <SelectItem value="balls-and-sticks">
                  Balls and Sticks
                </SelectItem>
                <SelectItem value="surface">Surface</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex gap-4 flex-col sm:flex-row">
          <div className="grow">
            <h3 className="font-bold mb-2">Coloring</h3>
            <Select>
              <SelectTrigger className="min-w-[180px] border-2">
                <SelectValue placeholder="Select Coloring" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="structure">Cartoon</SelectItem>
                <SelectItem value="charges-relative">
                  Charges (relative)
                </SelectItem>
                <SelectItem value="charges-absolute">
                  Charges (absolute)
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="w-full col-span-1 sm:w-1/2">
            <h3 className="mb-2 w-fit">Max Value</h3>
            <div className="flex gap-4">
              <Input type="number" className="border-2 lg:min-w-[120px]" />
              <Button type="reset" variant={"secondary"}>
                Reset
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
