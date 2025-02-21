import { BrowserRouter, Route, Routes } from "react-router";
import { Home } from "./pages/home";
import { Setup } from "./pages/setup";
import { Results } from "./pages/results";
import { Layout } from "./components/layout/layout";

export const routes = ["setup", "results"] as const;
export type Acc2Route = (typeof routes)[number];

export const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="setup" element={<Setup />} />
          <Route path="results" element={<Results />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
