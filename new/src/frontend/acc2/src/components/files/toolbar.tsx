import { SearchInput } from "../shared/search-input";
import { FilesFilters, isValidFilesOrderField } from "@acc2/api/types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Button } from "../ui/button";
import { ArrowUpZA, ArrowDownZA } from "lucide-react";

export type FilesToolbarProps = {
  filters: FilesFilters;
  setFilters: React.Dispatch<React.SetStateAction<FilesFilters>>;
};

export const FilesToolbar = ({ filters, setFilters }: FilesToolbarProps) => {
  return (
    <div className="mb-2 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
      <SearchInput
        searchKey="search"
        type="text"
        placeholder="Search ..."
        className="min-w-[100px] w-full sm:w-[360px]"
        onSearch={(search) => {
          setFilters((filters) => ({ ...filters, search }));
        }}
      />
      <div className="flex gap-2 w-full sm:w-fit">
        <Select
          defaultValue="uploaded_at"
          onValueChange={(orderBy) => {
            if (!isValidFilesOrderField(orderBy)) {
              return;
            }
            setFilters((filters) => ({ ...filters, orderBy: orderBy }));
          }}
        >
          <SelectTrigger className="sm:w-[180px] border-2">
            <SelectValue placeholder="Order By" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="uploaded_at">Date</SelectItem>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="size">Size</SelectItem>
          </SelectContent>
        </Select>
        <Button
          onClick={() =>
            setFilters((filters) => ({
              ...filters,
              order: filters.order === "asc" ? "desc" : "asc",
            }))
          }
        >
          {filters.order === "asc" && <ArrowUpZA />}
          {filters.order === "desc" && <ArrowDownZA />}
        </Button>
      </div>
    </div>
  );
};
