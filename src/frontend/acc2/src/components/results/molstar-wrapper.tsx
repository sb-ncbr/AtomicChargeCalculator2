import MolstarPartialCharges from "@acc2/lib/viewer/viewer";
import { PluginUIContext } from "molstar/lib/commonjs/mol-plugin-ui/context";
import { HTMLAttributes, useEffect, useState } from "react";

import { Busy, BusySize } from "../shared/busy";
import { MolstarViewer } from "./molstar";

export type MolstarWrapperProps = {
  setMolstar: React.Dispatch<
    React.SetStateAction<MolstarPartialCharges | undefined>
  >;
} & HTMLAttributes<HTMLElement>;

export const MolstarWrapper = ({ setMolstar }: MolstarWrapperProps) => {
  const [plugin, setPlugin] = useState<PluginUIContext | undefined>();

  const setup = async () => {
    const molstar = await MolstarPartialCharges.initialize();

    setMolstar(molstar);
    setPlugin(molstar.plugin);
  };

  useEffect(() => {
    void setup();
  }, []);

  return (
    <div className="relative w-4/5 mx-auto">
      <Busy isBusy={!plugin} size={BusySize.Big} />
      {plugin && <MolstarViewer plugin={plugin} />}
    </div>
  );
};
