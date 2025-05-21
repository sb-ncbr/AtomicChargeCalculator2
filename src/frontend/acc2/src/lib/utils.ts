import { type ClassValue, clsx } from "clsx";
import { formatBytes as format } from "molstar/lib/commonjs/mol-util";
import { twMerge } from "tailwind-merge";

export const cn = (...inputs: ClassValue[]): string => {
  return twMerge(clsx(inputs));
};

export const downloadBlob = (data: Blob, filename: string): void => {
  const href = URL.createObjectURL(data);
  const link = document.createElement("a");

  link.href = href;
  link.download = filename;
  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  URL.revokeObjectURL(href);
};

export const formatBytes = (bytes: number): string => {
  if (bytes === 0) {
    return "0";
  }

  return format(bytes);
};
