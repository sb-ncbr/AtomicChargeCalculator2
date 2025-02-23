import { Results } from "@acc2/components/results/results";
import { useTitle } from "@acc2/hooks/use-title";
import { useNavigate, useSearchParams } from "react-router";

export const ResultsPage = () => {
  useTitle("Results");

  const [searchParams, _setSearchParams] = useSearchParams();
  const navigator = useNavigate();

  const computationId = searchParams.get("comp_id");
  if (!computationId) {
    navigator("/");
    return null;
  }

  return <Results computationId={computationId} />;
};
