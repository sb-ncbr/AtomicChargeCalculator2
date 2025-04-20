import { useFormContext } from "react-hook-form";

import { InfoTooltip } from "../setup/info-tooltip";
import { FormControl, FormField, FormItem, FormLabel } from "../ui/form";
import { Switch } from "../ui/switch";

export const AdvancedSettings = () => {
  const form = useFormContext();

  return (
    <div className="flex flex-col gap-2">
      <FormField
        control={form.control}
        name="settings.readHetatm"
        render={({ field }) => (
          <FormItem className="flex gap-2 items-center">
            <FormControl>
              <Switch checked={field.value} onCheckedChange={field.onChange} />
            </FormControl>
            <FormLabel className="font-bold">
              Read HETATM
              <InfoTooltip info="Read HETATM records from PDB/mmCIF files." />
            </FormLabel>
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="settings.ignoreWater"
        render={({ field }) => (
          <FormItem className="flex gap-2 items-center">
            <FormControl>
              <Switch checked={field.value} onCheckedChange={field.onChange} />
            </FormControl>
            <FormLabel className="font-bold">
              Ignore water
              <InfoTooltip info="Discard water molecules from PDB/mmCIF files." />
            </FormLabel>
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="settings.permissiveTypes"
        render={({ field }) => (
          <FormItem className="flex gap-2 items-center">
            <FormControl>
              <Switch checked={field.value} onCheckedChange={field.onChange} />
            </FormControl>
            <FormLabel className="font-bold">
              Permissive types
              <InfoTooltip info="Use similar parameters for similar atom/bond types if no exact match is found." />
            </FormLabel>
          </FormItem>
        )}
      />
    </div>
  );
};
