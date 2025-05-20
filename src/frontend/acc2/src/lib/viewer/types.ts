// The following code is modified from the original molstar-partial-charges library,
// available here: https://github.com/MergunFrimen/molstar-partial-charges/blob/master/src/types.ts

import { StructureRepresentationRegistry } from "molstar/lib/commonjs/mol-repr/structure/registry";
import { ColorTheme } from "molstar/lib/commonjs/mol-theme/color";
import { SizeTheme } from "molstar/lib/commonjs/mol-theme/size";

export type Representation3D = {
  colorTheme: Color;
  type: Type;
  sizeTheme: Size;
};

export type Type = {
  name: StructureRepresentationRegistry.BuiltIn | "default";
  params: StructureRepresentationRegistry.BuiltInParams<StructureRepresentationRegistry.BuiltIn>;
};
export type Color = {
  name:
    | ColorTheme.BuiltIn
    | "sb-ncbr-partial-charges"
    | "plddt-confidence"
    | "default";
  params: ColorTheme.BuiltInParams<ColorTheme.BuiltIn>;
};
export type Size = {
  name: SizeTheme.BuiltIn;
  params: SizeTheme.BuiltInParams<SizeTheme.BuiltIn>;
};

export type AtomKey = {
  labelCompId: string;
  labelSeqId: number;
  labelAtomId: string;
};

export type TargetWebApp = "AlphaCharges" | "ACC2";

export type Extensions = {
  MAQualityAssessment?: boolean;
  SbNcbrPartialCharges?: boolean;
};
