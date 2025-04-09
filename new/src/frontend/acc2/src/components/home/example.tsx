import { PropsWithChildren } from "react";

import { Button } from "../ui/button";
import { Card } from "../ui/card";

export type ExampleProps = PropsWithChildren & {
  title: string;
  image: { src: string; alt: string };
  actions: { name: string; action: () => void }[];
};

export const Example = ({ title, image, actions, children }: ExampleProps) => {
  return (
    <Card className="border p-4 flex flex-col rounded-none grow">
      <h3 className="font-bold text-lg mb-8 text-center capitalize">{title}</h3>
      <div className="flex gap-8 items-center flex-col grow">
        <div className="h-[220px] flex items-center justify-center">
          <img src={image.src} alt={image.alt} />
        </div>
        {children}
        <div className="flex gap-4 grow items-end">
          {actions.map(({ name, action }, index) => (
            <Button key={index} type="button" onClick={action}>
              {name}
            </Button>
          ))}
        </div>
      </div>
    </Card>
  );
};
