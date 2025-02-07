import { Button } from "@acc2/components/ui/button";
import { Card } from "@acc2/components/ui/card";
import { Input } from "@acc2/components/ui/input";
import { Label } from "@acc2/components/ui/label";
import { useNavigate } from "react-router";

export const Compute = () => {
  const navigate = useNavigate();

  return (
    <Card className="w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mb-12 mt-0 xs:mt-8 md:mt-0">
      <h2 className="text-5xl text-primary font-bold">Compute</h2>
      <form action={() => navigate("/results")}>
        <div className="my-4 flex flex-col gap-2">
          <Label className="font-bold text-lg">Upload structures</Label>
          <Input
            id="files"
            type="file"
            accept=".sdf,.mol2,.pdb,.mmcif"
            multiple
            className="border-2 border-primary cursor-pointer xs:w-fit"
          />
          <p className="text-sm text-black text-opacity-40">
            Supported filetypes are <span className="font-bold">sdf</span>,
            <span className="font-bold"> mol2</span>,
            <span className="font-bold"> pdb</span>,
            <span className="font-bold"> mmcif</span>. You can upload one or
            multiple files at the same time. Maximum allowed upload size is
            <span className="font-bold"> 250MB</span>.
          </p>
        </div>
        <div className="flex gap-4 flex-col xs:flex-row">
          <Button type="submit">Compute</Button>
          <Button
            type="button"
            variant={"secondary"}
            onClick={() => navigate("/setup")}
          >
            Setup Computation
          </Button>
        </div>
      </form>
    </Card>
  );
};
