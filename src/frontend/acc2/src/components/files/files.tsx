import { FileResponse } from "@acc2/api/files/types";
import { useFileFilters } from "@acc2/lib/hooks/filters/use-file-filters";
import { useQuotaQuery } from "@acc2/lib/hooks/queries/use-files";
import { useFilesQuery } from "@acc2/lib/hooks/queries/use-files";
import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import { useEffect, useState } from "react";

import { Busy } from "../shared/busy";
import { Paginator } from "../shared/paginator";
import { QuotaProgress } from "../shared/quota-progress";
import { ComputeDialog } from "./compute-dialog";
import { File } from "./file";
import { SelectedFiles } from "./selected-files";
import { FilesToolbar } from "./toolbar";
import { UploadDialog } from "./upload-dialog";

dayjs.extend(localizedFormat);

export const Files = () => {
  const { filters, setFilters } = useFileFilters();

  const {
    data: quota,
    isPending: isQuotaPending,
    isError: isQuotaError,
  } = useQuotaQuery();
  const {
    data: files,
    refetch,
    isPending: isFilesPending,
    isError: isFilesError,
    isFetching: isFilesFetching,
  } = useFilesQuery(filters);

  const [selectedFiles, setSelectedFiles] = useState<FileResponse[]>([]);

  useEffect(() => {
    void refetch({ cancelRefetch: false });
  }, [filters, refetch]);

  return (
    <main className="min-h-main w-full max-w-content mx-auto flex flex-col p-4">
      <h2 className="text-3xl text-primary font-bold mb-2 md:text-5xl">
        Uploaded Files
      </h2>

      <Busy
        isBusy={isFilesPending || isQuotaPending || isFilesFetching}
        fullscreen
      >
        Loading files
      </Busy>

      <div className="w-full flex items-center gap-4">
        {quota && <QuotaProgress quota={quota} />}
      </div>

      <div className="flex gap-2">
        <UploadDialog />
        <ComputeDialog files={selectedFiles} />
      </div>

      <SelectedFiles
        selectedFiles={selectedFiles}
        setSelectedFiles={setSelectedFiles}
      />

      <FilesToolbar filters={filters} setFilters={setFilters} />

      {(isFilesError || isQuotaError) && (
        <div className="grid place-content-center grow">
          <span className="font-bold text-2xl">
            Something went wrong while fetching files.
          </span>
        </div>
      )}

      {files && files.items.length === 0 && (
        <div className="grid place-content-center grow">
          <span className="font-bold text-2xl">No files to show.</span>
        </div>
      )}

      {files && files.items.length > 0 && (
        <>
          {files.items.map((file, index) => (
            <File
              file={file}
              isSelected={
                !!selectedFiles.find(
                  (selectedFile: FileResponse) =>
                    selectedFile.fileHash === file.fileHash
                )
              }
              onFileSelect={(selectedFile, checked) => {
                if (checked) {
                  setSelectedFiles((files) => [...files, file]);
                } else {
                  setSelectedFiles((files) =>
                    files.filter(
                      (file) => selectedFile.fileHash != file.fileHash
                    )
                  );
                }
              }}
              key={`${index}-${file.fileHash}`}
            />
          ))}
          <Paginator
            page={files.page}
            pageSize={files.pageSize}
            totalPages={files.totalPages}
            onPageChange={({ page, pageSize }) =>
              setFilters((filters) => ({ ...filters, page, pageSize }))
            }
            className="mt-auto"
          />
        </>
      )}
    </main>
  );
};
