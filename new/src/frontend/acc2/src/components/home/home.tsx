import { ScrollArea } from "@acc2/components/ui/scroll-area";
import { Banner } from "@acc2/components/home/banner";
import { Compute } from "@acc2/components/home/sections/compute";
import { About } from "@acc2/components/home/sections/about";
import { Examples } from "@acc2/components/home/sections/examples";
import { Citing } from "@acc2/components/home/sections/citing";
import { License } from "@acc2/components/home/sections/license";
import { Elixir } from "@acc2/components/home/sections/elixir";

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
