import { Method } from "@acc2/api/methods/types";
import { Parameters } from "@acc2/api/parameters/types";
import { usePublicationQuery } from "@acc2/lib/hooks/queries/use-publication";

import { Busy } from "../shared/busy";

export type PublicationProps = {
  publicationSource: Parameters | Method;
};

export const Publication = ({ publicationSource }: PublicationProps) => {
  const { data: publication, isPending } =
    usePublicationQuery(publicationSource);

  const parsePublication = (publication: string) => {
    const doiRegex = /doi:(.*)/;
    const doi = publication.match(doiRegex)?.[1] ?? "";

    return {
      text: publication.replace(doiRegex, ""),
      url: `https://doi.org/${doi}`,
      doi,
    };
  };

  const publicationInfo = parsePublication(publication ?? "");

  return (
    <>
      {publication && (
        <div className="relative">
          <Busy isBusy={isPending} />
          <h4 className="text-sm font-bold">Publication</h4>
          <p className="text-sm">
            {publicationInfo.text}
            <a
              href={publicationInfo.url}
              target="_blank"
              className="text-primary hover:underline" rel="noreferrer"
            >
              doi:{publicationInfo.doi}
            </a>
          </p>
        </div>
      )}
    </>
  );
};
