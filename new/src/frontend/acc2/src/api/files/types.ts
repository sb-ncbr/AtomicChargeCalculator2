import { MoleculeSetStats } from "../calculations/types";

export type UploadResponse = {
  file: string;
  file_hash: string;
}[];

export type QuotaResponse = {
  usedSpace: number;
  availableSpace: number;
  quota: number;
};

export type FileResponse = {
  fileHash: string;
  fileName: string;
  size: number;
  stats: MoleculeSetStats;
  uploadedAt: string;
};
