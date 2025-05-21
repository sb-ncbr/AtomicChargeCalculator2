import { Banner } from "@acc2/components/home/banner";
import { About } from "@acc2/components/home/sections/about";
import { Citing } from "@acc2/components/home/sections/citing";
import { Compute } from "@acc2/components/home/sections/compute";
import { Elixir } from "@acc2/components/home/sections/elixir";
import { Examples } from "@acc2/components/home/sections/examples";
import { License } from "@acc2/components/home/sections/license";
import { ScrollArea } from "@acc2/components/ui/scroll-area";

export const Home = () => {
  return (
    <main className="mx-auto w-full selection:text-white selection:bg-primary">
      <ScrollArea type="auto">
        <Banner />
        <Compute />
        <About />
        <Examples />
        <Citing />
        <License />
        <Elixir />
      </ScrollArea>
    </main>
  );
};
