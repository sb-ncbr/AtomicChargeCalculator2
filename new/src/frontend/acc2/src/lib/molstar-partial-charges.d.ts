declare module "molstar-partial-charges" {
  import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
  import { BuiltInTrajectoryFormat } from "molstar/lib/mol-plugin-state/formats/trajectory";

  export interface AtomKey {
    chainId?: string;
    residueNumber?: number;
    atomName?: string;
  }

  export interface Extensions {
    [key: string]: any;
  }

  export type TargetWebApp = string;

  export default class MolstarPartialCharges {
    plugin: PluginUIContext;
    constructor(plugin: PluginUIContext);
    static create(
      target: string,
      extensions?: Extensions
    ): Promise<MolstarPartialCharges>;
    load(
      url: string,
      format?: BuiltInTrajectoryFormat,
      targetWebApp?: TargetWebApp
    ): Promise<void>;

    charges: {
      getMethodNames: () => (string | undefined)[];
      getTypeId: () => number;
      setTypeId: (typeId: number) => void;
      getMaxCharge: () => number;
    };

    color: {
      default: () => Promise<void>;
      alphaFold: () => Promise<void>;
      absolute: (max: number) => Promise<void>;
      relative: () => Promise<void>;
    };

    type: {
      isDefaultApplicable: () => boolean;
      default: () => Promise<void>;
      ballAndStick: () => Promise<void>;
      surface: () => Promise<void>;
    };

    visual: {
      focus: (key: AtomKey) => void;
    };
  }
}
