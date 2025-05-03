import { Method } from "@acc2/api/methods/types";

import { Publication } from "../publication";

type MethodPublicationProps = {
  method?: Method;
};

export const MethodPublication = ({ method }: MethodPublicationProps) => {
  return (
    <>
      <h4 className="text-sm font-bold">Full Name</h4>
      <p className="text-sm mb-2">{method?.fullName}</p>
      {method && <Publication publicationSource={method} />}
    </>
  );
};
