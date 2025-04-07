import { Method } from "@acc2/api/methods/types";
import { Parameters } from "@acc2/api/parameters/types";
import { useQuery } from "@tanstack/react-query";

export const usePublicationQuery = (data?: Parameters | Method) => {
  return useQuery({
    queryKey: ["publication", data?.internalName],
    queryFn: async () => {
      const { default: publicationData } = await import(
        "@acc2/assets/publication_info.json"
      );
      if (data?.publication && data.publication in publicationData) {
        return publicationData[
          data.publication as keyof typeof publicationData
        ];
      } else {
        return "";
      }
    },
  });
};
