import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "../ui/hover-card";

export type HoverDetailsListProps = {
  trigger: React.ReactNode;
  data: { [label: string]: string | number };
};

export const HoverDetailsList = ({ data, trigger }: HoverDetailsListProps) => {
  return (
    <HoverCard openDelay={200} closeDelay={0}>
      <HoverCardTrigger asChild>{trigger}</HoverCardTrigger>
      <HoverCardContent>
        <div className="w-fit flex flex-col gap-2">
          {Object.entries(data).map(([label, value]) => (
            <div className="flex flex-col">
              <span className="font-bold text-sm">{label}</span>
              <span className="text-xs">{value}</span>
            </div>
          ))}
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};
