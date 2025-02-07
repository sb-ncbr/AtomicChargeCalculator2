import { Banner } from "./banner";
import { ScrollArea } from "../ui/scroll-area";
import { Compute } from "./sections/compute";
import { About } from "./sections/about";
import { Examples } from "./sections/examples";
import { Citing } from "./sections/citing";
import { License } from "./sections/license";
import { Elixir } from "./sections/elixir";

export const Main = () => {
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
