import { Footer } from "@acc2/components/layout/footer";
import { Header } from "@acc2/components/layout/header/header";
import { Main } from "@acc2/components/home/main";
import { useTitle } from "@acc2/hooks/use-title";

export const Home = () => {
  useTitle("Home");
  return (
    <>
      {/* TODO: Use layout */}
      <Header />
      <Main />
      <Footer />
    </>
  );
};
