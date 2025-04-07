import { FileResponse } from "@acc2/api/files/types";
import { Badge } from "../ui/badge";
import { X } from "lucide-react";

export type SelectedFilesProps = {
  selectedFiles: FileResponse[];
  setSelectedFiles: React.Dispatch<React.SetStateAction<FileResponse[]>>;
};

export const SelectedFiles = ({
  selectedFiles,
  setSelectedFiles,
}: SelectedFilesProps) => {
  return (
    <div className="my-2 min-h-7">
      <span className="text-sm mr-2">Selected Files:</span>
      {selectedFiles.map((file) => (
        <Badge
          key={`selected-${file.fileHash}`}
          variant={"secondary"}
          className="mr-2 rounded"
        >
          {file.fileName}
          <X
            height={10}
            width={10}
            className="cursor-pointer ml-2 hover:scale-125"
            onClick={() =>
              setSelectedFiles((files) =>
                files.filter(
                  (selectedFile) => selectedFile.fileHash !== file.fileHash
                )
              )
            }
          />
        </Badge>
      ))}
    </div>
  );
};
