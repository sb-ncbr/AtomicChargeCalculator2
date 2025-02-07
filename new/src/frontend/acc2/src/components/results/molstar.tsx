import MolstarPartialCharges from "molstar-partial-charges";
import { HTMLAttributes, useEffect } from "react";
import { Card } from "../ui/card";
import { cn } from "@acc2/lib/utils";

export type MolstarProps = {} & HTMLAttributes<HTMLElement>;

export const MolStarWrapper = ({ className, ...props }: MolstarProps) => {
  const setup = async () => {
    const molstar = await MolstarPartialCharges.create("molstar", {
      SbNcbrPartialCharges: true,
    });

    try {
      await molstar.load(
        `${location.origin}/propofol.fw2.cif`,
        "mmcif",
        "ACC2"
      );
    } catch (e) {
      console.log("Caught error", e);
    }
    await molstar.color.relative();
    await molstar.type.ballAndStick();
  };

  useEffect(() => {
    setup();
  }, []);

  return (
    <Card
      {...props}
      className={cn(
        "w-4/5 rounded-none shadow-xl mx-auto p-4 max-w-content mt-4 flex flex-col h-[700px]",
        className
      )}
    >
      <div className="w-full h-full relative">
        <div id="molstar"></div>
      </div>
    </Card>
  );
};
