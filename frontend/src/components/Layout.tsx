import { Outlet } from "react-router-dom";

import Footer from "./Footer.tsx";
import Navbar from "./Navbar.tsx";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
