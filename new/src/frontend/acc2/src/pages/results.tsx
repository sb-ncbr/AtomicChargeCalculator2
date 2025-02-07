import { Footer } from "@acc2/components/layout/footer";
import { Header } from "@acc2/components/layout/header/header";
import { Main } from "@acc2/components/results/main";
import { useTitle } from "@acc2/hooks/use-title";

export const Results = () => {
  useTitle("Results");
  return (
    <>
      {/* TODO: Use layout */}
      <Header />
      <Main />
      <Footer />
    </>
  );
};
