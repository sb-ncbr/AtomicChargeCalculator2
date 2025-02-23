import { useTitle } from "@acc2/hooks/use-title";
import { Home } from "@acc2/components/home/home";

export const HomePage = () => {
  useTitle("Home");

  return <Home />;
};
