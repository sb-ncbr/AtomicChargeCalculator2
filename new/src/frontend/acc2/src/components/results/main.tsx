import { MolStarWrapper } from "./molstar";
import { Controls } from "./controls";
import { ScrollArea } from "../ui/scroll-area";

export const Main = () => {
  return (
    <main className="mx-auto w-full selection:text-white selection:bg-primary mb-8">
      <ScrollArea type="auto">
        <h2 className="w-4/5 mx-auto max-w-content mt-8 text-3xl text-primary font-bold mb-2 sm:text-5xl">
          Computational Results
        </h2>
        <Controls />
        <MolStarWrapper />
      </ScrollArea>
    </main>
  );
};
