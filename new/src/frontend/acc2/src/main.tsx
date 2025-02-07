import { BrowserRouter, Route, Routes } from "react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Setup } from "./pages/setup";
import { Home } from "./pages/home";
import { Results } from "./pages/results";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      {/* TODO: move routes */}
      <Routes>
        <Route index element={<Home />} />
        <Route path="/setup" element={<Setup />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
