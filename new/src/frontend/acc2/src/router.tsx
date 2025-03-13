import { BrowserRouter, Route, Routes } from "react-router";
import { HomePage } from "./pages/home";
import { SetupPage } from "./pages/setup";
import { ResultsPage } from "./pages/results";
import { Layout } from "./components/layout/layout";
import { CalculationsPage } from "./pages/calculations";

export const routes = ["setup", "results"] as const;
export type Acc2Route = (typeof routes)[number];

export const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="setup" element={<SetupPage />} />
          <Route path="results" element={<ResultsPage />} />
          <Route path="calculations" element={<CalculationsPage />} />
          <Route path="*" element={<HomePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
