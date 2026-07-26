import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";

import CalculatorPage from "./components/CalculatorPage.tsx";
import Layout from "./components/Layout.tsx";
import CableSizing from "./pages/calculators/CableSizing.tsx";
import CoolingLoad from "./pages/calculators/CoolingLoad.tsx";
import Home from "./pages/Home.tsx";
import Modules from "./pages/Modules.tsx";
import NotFound from "./pages/NotFound.tsx";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pathname]);
  return null;
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/modules" element={<Modules />} />
          <Route path="/calc/cable-sizing" element={<CableSizing />} />
          <Route path="/calc/cooling-load" element={<CoolingLoad />} />
          <Route path="/calc/:slug" element={<CalculatorPage />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </>
  );
}
