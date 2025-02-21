import { Calculations } from "@acc2/components/setup/calculations";
import { Method } from "@acc2/components/setup/method";
import { Parameters } from "@acc2/components/setup/parameters";
import { Button } from "@acc2/components/ui/button";
import { Card } from "@acc2/components/ui/card";
import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { Separator } from "@acc2/components/ui/separator";
import { useTitle } from "@acc2/hooks/use-title";
import { useNavigate, useSearchParams } from "react-router";

export const Setup = () => {
  useTitle("Setup");

  const navigate = useNavigate();
  const [searchParams, _] = useSearchParams();
  const computationId = searchParams.get("comp_id");

  if (!computationId) {
    navigate("/");
    return null;
  }

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
            <Method computationId={computationId} />
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
