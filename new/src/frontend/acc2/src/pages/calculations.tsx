import { Calculations } from "@acc2/components/calculations/calculations";
import { useTitle } from "@acc2/hooks/use-title";

export const CalculationsPage = () => {
  useTitle("Calculations");

  return <Calculations />;
};
