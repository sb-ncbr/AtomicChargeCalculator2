import { Results } from "@acc2/components/results/results";
import { useTitle } from "@acc2/lib/hooks/use-title";
import { useNavigate, useSearchParams } from "react-router";

export const ResultsPage = () => {
  useTitle("Results");

  const [searchParams, _setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const computationId = searchParams.get("comp_id");
  const exampleId = searchParams.get("example_id");
  if (!computationId && !exampleId) {
    navigate("/");
    return null;
  }

  if (exampleId) {
    return <Results computationId={`examples/${exampleId}`} />;
  }

  return <Results computationId={computationId!} />;
};
