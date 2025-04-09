import { Home } from "@acc2/components/home/home";
import { useTitle } from "@acc2/lib/hooks/use-title";

export const HomePage = () => {
  useTitle("Home");

  return <Home />;
};
