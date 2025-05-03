import { Parameters } from "../parameters/types";

export const MethodTypes = {
  "2D": "2D",
  "3D": "3D",
  OTHER: "other",
} as const;

export type MethodType = (typeof MethodTypes)[keyof typeof MethodTypes];

export type Method = {
  name: string;
  internalName: string;
  fullName: string;
  publication: string | null;
  type: MethodType;
  hasParameters: boolean;
};

export type SuitableMethods = {
  methods: Method[];
  parameters: Record<Method["internalName"], Parameters[]>;
};
