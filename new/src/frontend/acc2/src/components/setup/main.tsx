import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Method } from "./method";
import { useNavigate } from "react-router";
import { Parameters } from "./parameters";
import { Calculations } from "./calculations";
import { Separator } from "../ui/separator";
import { ScrollArea } from "../ui/scroll-area";

export const Main = () => {
  const navigate = useNavigate();

  return (
    <main className="mx-auto w-full selection:text-white selection:bg-primary mb-12">
      <ScrollArea type="auto" className="h-full">
        <Card className="w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mt-12 flex flex-col">
          <h2 className="text-3xl text-primary font-bold mb-2 md:text-5xl">
            Computation Settings
          </h2>
          <p className="text-sm text-foreground/50">
            Note that the list of methods and parameters shows only suitable
            combinations for given input structures. See the complete list of
            parameters.
          </p>
          <div className="grid grid-cols-1 xxl:grid-cols-2 gap-4">
            <Method />
            <Parameters />
          </div>
          <Button className="mt-4 self-start" variant={"secondary"}>
            Add To Calculation
          </Button>
          <Separator className="my-4" />
          <Calculations />
          <div className="self-start mt-4">
            <Button className="mr-4" onClick={() => navigate("/results")}>
              Compute
            </Button>
            <Button variant={"secondary"} onClick={() => navigate("/")}>
              Back
            </Button>
          </div>
        </Card>
      </ScrollArea>
    </main>
  );
};
