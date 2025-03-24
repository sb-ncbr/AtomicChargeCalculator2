import { SetStateAction } from "react";
import { Card } from "../ui/card";
import { Switch } from "../ui/switch";
import { InfoTooltip } from "./info-tooltip";

type SetupSettings = {
  readHetatm: boolean;
  ignoreWater: boolean;
  permissiveTypes: boolean;
};

export type SetupSettingsProps = {
  settings: SetupSettings;
  setSettings: React.Dispatch<SetStateAction<SetupSettings>>;
};

export const SetupSettings = ({
  settings,
  setSettings,
}: SetupSettingsProps) => {
  const onCheckedChange = (prop: keyof typeof settings, value: boolean) => {
    setSettings((settings) => ({ ...settings, [prop]: value }));
  };

  return (
    <Card className="flex gap-4 rounded-none p-4 mt-4 flex-wrap">
      <div className="flex gap-2 items-center">
        <Switch
          id="read-hetatm"
          checked={settings.readHetatm}
          onCheckedChange={(readHetatm) =>
            onCheckedChange("readHetatm", readHetatm)
          }
        />
        <label htmlFor="read-hetatm" className="font-bold">
          Read HETATM
          <InfoTooltip info="Read HETATM records from PDB/mmCIF files." />
        </label>
      </div>
      <div className="flex gap-2 items-center">
        <Switch
          id="ignore-water"
          checked={settings.ignoreWater}
          onCheckedChange={(ignoreWater) =>
            onCheckedChange("ignoreWater", ignoreWater)
          }
        />
        <label htmlFor="ignore-water" className="font-bold">
          Ignore water
          <InfoTooltip info="Discard water molecules from PDB/mmCIF files." />
        </label>
      </div>
      <div className="flex gap-2 items-center">
        <Switch
          id="permissive-types"
          checked={settings.permissiveTypes}
          onCheckedChange={(permissiveTypes) =>
            onCheckedChange("permissiveTypes", permissiveTypes)
          }
        />
        <label htmlFor="permissive-types" className="font-bold">
          Permissive types
          <InfoTooltip info="Use similar parameters for similar atom/bond types if no exact match is found." />
        </label>
      </div>
    </Card>
  );
};
