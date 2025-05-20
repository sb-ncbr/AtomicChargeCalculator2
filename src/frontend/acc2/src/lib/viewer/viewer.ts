// The following code is modified from the original molstar-partial-charges library,
// available here: https://github.com/MergunFrimen/molstar-partial-charges/blob/master/src/viewer.ts

import merge from "lodash.merge";
import { PLDDTConfidenceColorThemeProvider } from "molstar/lib/commonjs/extensions/model-archive/quality-assessment/color/plddt";
import { SbNcbrPartialCharges } from "molstar/lib/commonjs/extensions/sb-ncbr/partial-charges/behavior";
import { SbNcbrPartialChargesColorThemeProvider } from "molstar/lib/commonjs/extensions/sb-ncbr/partial-charges/color";
import { SbNcbrPartialChargesPropertyProvider } from "molstar/lib/commonjs/extensions/sb-ncbr/partial-charges/property";
import { MmcifFormat } from "molstar/lib/commonjs/mol-model-formats/structure/mmcif";
import {
  Model,
  StructureSelection,
} from "molstar/lib/commonjs/mol-model/structure";
import { BuiltInTrajectoryFormat } from "molstar/lib/commonjs/mol-plugin-state/formats/trajectory";
import { PluginUIContext } from "molstar/lib/commonjs/mol-plugin-ui/context";
import {
  DefaultPluginUISpec,
  PluginUISpec,
} from "molstar/lib/commonjs/mol-plugin-ui/spec";
import { StructureFocusRepresentation } from "molstar/lib/commonjs/mol-plugin/behavior/dynamic/selection/structure-focus-representation";
import { PluginConfig } from "molstar/lib/commonjs/mol-plugin/config";
import { PluginSpec } from "molstar/lib/commonjs/mol-plugin/spec";
import { BallAndStickRepresentationProvider } from "molstar/lib/commonjs/mol-repr/structure/representation/ball-and-stick";
import { GaussianSurfaceRepresentationProvider } from "molstar/lib/commonjs/mol-repr/structure/representation/gaussian-surface";
import { Script } from "molstar/lib/commonjs/mol-script/script";
import { ElementSymbolColorThemeProvider } from "molstar/lib/commonjs/mol-theme/color/element-symbol";
import { PhysicalSizeThemeProvider } from "molstar/lib/commonjs/mol-theme/size/physical";

import {
  AtomKey,
  Color,
  Representation3D,
  Size,
  TargetWebApp,
  Type,
} from "./types";

import "molstar/lib/mol-plugin-ui/skin/light.scss";

export default class MolstarPartialCharges {
  constructor(public plugin: PluginUIContext) {}

  static async initialize() {
    const defaultSpecs = DefaultPluginUISpec();
    const specs: PluginUISpec = {
      behaviors: [...defaultSpecs.behaviors],
      components: {
        ...defaultSpecs.components,
        remoteState: "none",
      },
      config: [[PluginConfig.Viewport.ShowAnimation, false]],

      layout: {
        initial: {
          isExpanded: false,
          showControls: false,
          regionState: {
            bottom: "full",
            left: "full",
            right: "full",
            top: "full",
          },
        },
      },
    };

    specs.behaviors.push(PluginSpec.Behavior(SbNcbrPartialCharges));

    const plugin = new PluginUIContext(specs);
    await plugin.init();

    return new MolstarPartialCharges(plugin);
  }

  async load(
    url: string,
    format: BuiltInTrajectoryFormat = "mmcif",
    targetWebApp: TargetWebApp = "ACC2"
  ) {
    await this.plugin.clear();

    const data = await this.plugin.builders.data.download(
      { url },
      { state: { isGhost: true } }
    );
    const trajectory = await this.plugin.builders.structure.parseTrajectory(
      data,
      format
    );
    await this.plugin.builders.structure.hierarchy.applyPreset(
      trajectory,
      "default",
      {
        showUnitcell: false,
        representationPreset: "auto",
      }
    );

    await this.setInitialRepresentationState(targetWebApp);

    if (format === "mmcif") {
      this.sanityCheck();
    }
  }

  charges = {
    getMethodNames: () => {
      const model = this.getModel();
      if (!model) throw new Error("No model found");
      const data = SbNcbrPartialChargesPropertyProvider.get(model).value;
      if (!data) throw new Error("No data found");
      const methodNames = [];
      for (let typeId = 1; typeId < data.typeIdToMethod.size + 1; ++typeId) {
        if (!data.typeIdToMethod.has(typeId))
          throw new Error(`Missing method for typeId ${typeId}`);
        methodNames.push(data.typeIdToMethod.get(typeId));
      }
      return methodNames;
    },
    getTypeId: () => {
      const model = this.getModel();
      if (!model) throw new Error("No model loaded.");
      const typeId = SbNcbrPartialChargesPropertyProvider.props(model).typeId;
      if (!typeId) throw new Error("No type id found.");
      return typeId;
    },
    setTypeId: (typeId: number) => {
      const model = this.getModel();
      if (!model) throw new Error("No model loaded.");
      if (!this.isTypeIdValid(model, typeId))
        throw new Error(`Invalid type id ${typeId}`);
      SbNcbrPartialChargesPropertyProvider.set(model, { typeId });
    },
    getMaxCharge: () => {
      const model = this.getModel();
      if (!model) throw new Error("No model loaded.");
      const maxCharge =
        SbNcbrPartialChargesPropertyProvider.get(model).value
          ?.maxAbsoluteAtomChargeAll;
      if (maxCharge === undefined)
        throw new Error("No max charge found for all charge sets.");
      return maxCharge;
    },
  };

  color = {
    default: async () => {
      await this.updateColor("default");
    },
    alphaFold: async () => {
      await this.updateColor(PLDDTConfidenceColorThemeProvider.name);
    },
    absolute: async (max: number) => {
      await this.updateColor(this.partialChargesColorProps.name, {
        maxAbsoluteCharge: max,
        absolute: true,
      });
    },
    relative: async () => {
      await this.updateColor(this.partialChargesColorProps.name, {
        absolute: false,
      });
    },
  };

  type = {
    isDefaultApplicable: () => {
      const other = ["cartoon", "carbohydrate"];
      return Array.from(this.defaultProps.values()).some(({ type }) =>
        other.includes(type.name)
      );
    },
    default: async () => {
      await this.updateType("default");
    },
    ballAndStick: async () => {
      await this.updateType(this.ballAndStickTypeProps.type.name);
    },
    surface: async () => {
      await this.updateType(this.surfaceTypeProps.type.name);
    },
  };
  behavior = {
    focus: (key: AtomKey) => {
      const data =
        this.plugin.managers.structure.hierarchy.current.structures[0]
          .components[0].cell.obj?.data;
      if (!data) return;

      const { labelCompId, labelSeqId, labelAtomId } = key;

      const selection = Script.getStructureSelection(
        (Q) =>
          Q.struct.generator.atomGroups({
            "atom-test": Q.core.logic.and([
              Q.core.rel.eq([
                Q.struct.atomProperty.macromolecular.label_comp_id(),
                labelCompId,
              ]),
              Q.core.rel.eq([
                Q.struct.atomProperty.macromolecular.label_seq_id(),
                labelSeqId,
              ]),
              Q.core.rel.eq([
                Q.struct.atomProperty.macromolecular.label_atom_id(),
                labelAtomId,
              ]),
            ]),
          }),
        data
      );

      const loci = StructureSelection.toLociWithSourceUnits(selection);
      this.plugin.managers.interactivity.lociHighlights.highlightOnly({ loci });
      this.plugin.managers.interactivity.lociSelects.selectOnly({ loci });
      this.plugin.managers.camera.focusLoci(loci);
      this.plugin.managers.structure.focus.setFromLoci(loci);
    },
    focusRange: (range: { residueStart: number; residueEnd: number }) => {
      const data =
        this.plugin.managers.structure.hierarchy.current.structures[0]
          .components[0].cell.obj?.data;
      if (!data) return;

      const { residueStart, residueEnd } = range;

      const selection = Script.getStructureSelection(
        (Q) =>
          Q.struct.generator.atomGroups({
            "residue-test": Q.core.rel.inRange([
              Q.struct.atomProperty.macromolecular.label_seq_id(),
              residueStart,
              residueEnd,
            ]),
          }),
        data
      );

      const loci = StructureSelection.toLociWithSourceUnits(selection);
      // this.plugin.managers.interactivity.lociHighlights.highlightOnly({ loci });
      this.plugin.managers.interactivity.lociSelects.selectOnly({ loci });
      this.plugin.managers.camera.focusLoci(loci);
      // this.plugin.managers.structure.focus.setFromLoci(loci);
    },
  };

  private readonly defaultProps: Map<string, Representation3D> = new Map();

  private readonly ballAndStickTypeProps: {
    type: Type;
    sizeTheme: Size;
  } = {
    type: {
      name: BallAndStickRepresentationProvider.name,
      params: {
        ...BallAndStickRepresentationProvider.defaultValues,
      },
    },
    sizeTheme: {
      name: PhysicalSizeThemeProvider.name,
      params: {
        ...PhysicalSizeThemeProvider.defaultValues,
      },
    },
  };
  private readonly surfaceTypeProps: {
    type: Type;
    sizeTheme: Size;
  } = {
    type: {
      name: GaussianSurfaceRepresentationProvider.name,
      params: {
        ...GaussianSurfaceRepresentationProvider.defaultValues,
        quality: "high",
      },
    },
    sizeTheme: {
      name: PhysicalSizeThemeProvider.name,
      params: {
        ...PhysicalSizeThemeProvider.defaultValues,
        scale: 1,
      },
    },
  };
  private readonly partialChargesColorProps: Color = {
    name: SbNcbrPartialChargesColorThemeProvider.name,
    params: {
      // not using default values
    },
  };
  private readonly elementSymbolColorProps: Color = {
    name: ElementSymbolColorThemeProvider.name,
    params: {
      ...ElementSymbolColorThemeProvider.defaultValues,
    },
  };
  private readonly plddtColorProps: Color = {
    name: PLDDTConfidenceColorThemeProvider.name,
    params: {
      ...PLDDTConfidenceColorThemeProvider.defaultValues,
    },
  };
  private readonly physicalSizeProps: Size = {
    name: PhysicalSizeThemeProvider.name,
    params: {
      ...PhysicalSizeThemeProvider.defaultValues,
    },
  };

  private async setInitialRepresentationState(targetWebApp: TargetWebApp) {
    this.defaultProps.clear();
    await this.plugin.dataTransaction(() => {
      for (const structure of this.plugin.managers.structure.hierarchy.current
        .structures) {
        for (const component of structure.components) {
          for (const representation of component.representations) {
            const params = representation.cell.transform.params;
            if (!params) continue;
            const { type } = params;
            this.defaultProps.set(representation.cell.transform.ref, {
              type: type as Type,
              colorTheme:
                targetWebApp === "AlphaCharges"
                  ? this.elementSymbolColorProps
                  : (params.colorTheme as Color),
              sizeTheme:
                targetWebApp === "AlphaCharges"
                  ? this.physicalSizeProps
                  : (params.sizeTheme as Size),
            });
          }
        }
      }
    });
  }

  private async updateType(name: Type["name"]) {
    await this.plugin.dataTransaction(async () => {
      for (const structure of this.plugin.managers.structure.hierarchy.current
        .structures) {
        const update = this.plugin.state.data.build();
        for (const component of structure.components) {
          for (const representation of component.representations) {
            let type, sizeTheme;

            if (!this.defaultProps.has(representation.cell.transform.ref))
              continue;

            if (name === this.ballAndStickTypeProps.type.name) {
              type = this.ballAndStickTypeProps.type;
              sizeTheme = this.ballAndStickTypeProps.sizeTheme;
            } else if (name === this.surfaceTypeProps.type.name) {
              type = this.surfaceTypeProps.type;
              sizeTheme = this.surfaceTypeProps.sizeTheme;
            } else if (name == "default") {
              type = this.defaultProps.get(
                representation.cell.transform.ref
              )?.type;
              sizeTheme = this.defaultProps.get(
                representation.cell.transform.ref
              )?.sizeTheme;
            } else {
              throw new Error("Invalid type theme");
            }

            const oldProps = representation.cell.transform.params;

            // switches to residue charge for certain representations
            const showResidueChargeFor = ["cartoon", "carbohydrate"];
            const typeName = type?.name;
            const showResidueCharge =
              typeName && showResidueChargeFor.includes(typeName);
            let colorTheme = oldProps?.colorTheme;
            colorTheme = merge({}, colorTheme, {
              params: { chargeType: showResidueCharge ? "residue" : "atom" },
            });

            const mergedProps = merge({}, oldProps, {
              type,
              sizeTheme,
              colorTheme,
            });
            update.to(representation.cell).update(mergedProps);
          }
        }
        await update.commit({ canUndo: "Update Theme" });
      }
      this.updateGranularity(name);
    });
  }

  private async updateColor(name: Color["name"], params: Color["params"] = {}) {
    await this.plugin.dataTransaction(async () => {
      for (const structure of this.plugin.managers.structure.hierarchy.current
        .structures) {
        const update = this.plugin.state.data.build();
        for (const component of structure.components) {
          for (const representation of component.representations) {
            let colorTheme;

            if (!this.defaultProps.has(representation.cell.transform.ref)) {
              colorTheme = this.elementSymbolColorProps;
            } else if (name === this.partialChargesColorProps.name) {
              colorTheme = this.partialChargesColorProps;
            } else if (name === this.plddtColorProps.name) {
              colorTheme = this.plddtColorProps;
            } else if (name === "default") {
              colorTheme = this.defaultProps.get(
                representation.cell.transform.ref
              )?.colorTheme;
            } else {
              throw new Error("Invalid color theme");
            }

            // switches to residue charge for certain representations
            const showResidueChargeFor = ["cartoon", "carbohydrate"];
            const typeName = representation.cell.transform.params?.type?.name;
            const showResidueCharge =
              typeName && showResidueChargeFor.includes(typeName);
            params = merge({}, params, {
              chargeType: showResidueCharge ? "residue" : "atom",
            });

            const oldProps = representation.cell.transform.params;
            const mergedProps = merge(
              {},
              oldProps,
              { colorTheme },
              { colorTheme: { params } }
            );
            update.to(representation.cell).update(mergedProps);
          }
        }
        await update.commit({ canUndo: "Update Theme" });
      }
      await this.updateFocusColorTheme(name, params);
    });
  }

  private sanityCheck() {
    // if (!this.plugin) throw new Error('No plugin found.');
    // if (!this.plugin.managers.structure.hierarchy.current.structures.length)
    //     throw new Error('No structure loaded.');
    const model = this.getModel();
    if (!model) throw new Error("No model loaded.");
    const sourceData = model.sourceData as MmcifFormat;
    const atomCount = model.atomicHierarchy.atoms._rowCount;
    const chargesCount =
      sourceData.data.frame.categories.sb_ncbr_partial_atomic_charges.rowCount;
    if (chargesCount > 0 && chargesCount % atomCount !== 0)
      throw new Error(
        `Atom count (${atomCount}) does not match charge count (${chargesCount}).`
      );
  }

  private updateGranularity(type: Type["name"]) {
    this.plugin.managers.interactivity.setProps({
      granularity: type === "default" ? "residue" : "element",
    });
  }

  private async updateFocusColorTheme(
    color: Color["name"],
    params: Color["params"] = {}
  ) {
    let props =
      color === SbNcbrPartialChargesColorThemeProvider.name
        ? this.partialChargesColorProps
        : this.elementSymbolColorProps;
    props = merge({}, props, { params: { ...params, chargeType: "atom" } });
    await this.plugin.state.updateBehavior(
      StructureFocusRepresentation,
      (p) => {
        p.targetParams.colorTheme = props;
        p.surroundingsParams.colorTheme = props;
      }
    );
  }

  private getModel() {
    return this.plugin.managers.structure.hierarchy.current.structures[0].model
      ?.cell?.obj?.data;
  }

  private isTypeIdValid(model: Model, typeId: number) {
    const sourceData = model.sourceData as MmcifFormat;
    const typeIds =
      sourceData.data.frame.categories.sb_ncbr_partial_atomic_charges_meta
        .getField("id")
        ?.toIntArray();
    return typeIds?.includes(typeId);
  }
}

declare global {
  interface Window {
    MolstarPartialCharges: typeof MolstarPartialCharges;
  }
}

window.MolstarPartialCharges = MolstarPartialCharges;
