import { Footer } from "@acc2/components/layout/footer";
import { Header } from "@acc2/components/layout/header/header";
import { Main } from "@acc2/components/setup/main";
import { useTitle } from "@acc2/hooks/use-title";

export const Setup = () => {
  useTitle("Setup");
  return (
    <>
      {/* TODO: Use layout */}
      <Header />
      <Main />
      <Footer />
    </>
  );
};
