import { ReactNode, useState } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../ui/alert-dialog";
import { Button } from "../ui/button";

export type ConfirmActionProps = {
  onConfirm: () => void;
  trigger: ReactNode;
  title?: string;
  description?: string;
};

export const ConfirmAction = ({
  onConfirm,
  title,
  description,
  trigger,
}: ConfirmActionProps) => {
  const [open, setOpen] = useState<boolean>(false);

  return (
    <AlertDialog open={open}>
      <AlertDialogTrigger
        onClick={(e) => {
          e.stopPropagation();
          setOpen(true);
        }}
        asChild
      >
        {trigger}
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title ?? "Confirmation"}</AlertDialogTitle>
          <AlertDialogDescription>
            {description ?? "Are you sure you want to perform this action?"}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel asChild>
            <Button
              variant={"ghost"}
              onClick={(e) => {
                e.stopPropagation();
                setOpen(false);
              }}
            >
              Cancel
            </Button>
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.stopPropagation();
              onConfirm();
              setOpen(false);
            }}
          >
            Continue
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
