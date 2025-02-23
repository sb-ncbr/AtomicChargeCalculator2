import { Setup } from "@acc2/components/setup/setup";
import { useTitle } from "@acc2/hooks/use-title";
import { useNavigate, useSearchParams } from "react-router";

export const SetupPage = () => {
  useTitle("Setup");

  const navigate = useNavigate();
  const [searchParams, _] = useSearchParams();

  const computationId = searchParams.get("comp_id");
  if (!computationId) {
    navigate("/");
    return null;
  }

  return <Setup computationId={computationId} />;
};
