import { Parameters } from "@acc2/api/parameters/types";

import { Publication } from "../publication";

export type ParametersPublicationProps = {
  parameters?: Parameters;
};

export const ParametersPublication = ({
  parameters,
}: ParametersPublicationProps) => {
  return <>{parameters && <Publication publicationSource={parameters} />}</>;
};
