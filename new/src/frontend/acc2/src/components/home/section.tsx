import { HTMLAttributes, PropsWithChildren } from "react";
import { Paperclip } from "lucide-react";
import { cn } from "@acc2/lib/utils";
import { Separator } from "../ui/separator";

export type SectionProps = {
  title?: string;
  separator?: boolean;
} & HTMLAttributes<HTMLElement> &
  PropsWithChildren;

export const Section = ({
  title,
  children,
  className,
  separator = true,
  ...props
}: SectionProps) => {
  const copySection = (id: string) =>
    navigator.clipboard.writeText(`${location.origin}/#${id}`);

  return (
    <>
      <section
        {...props}
        className={cn(
          "w-4/5 mx-auto px-4 max-w-content -mt-[100px] pt-[100px]",
          className
        )}
        id={title?.toLowerCase()}
      >
        {title && (
          <h2 className="group text-5xl text-primary font-bold ml-[1/5] mb-4">
            {title}
            <Paperclip
              className="ml-4 hidden group-hover:inline-block cursor-pointer"
              onClick={() => copySection(title?.toLowerCase())}
            />
          </h2>
        )}
        {children}
      </section>
      {separator && <Separator className="my-12" />}
    </>
  );
};
