import { Link } from "react-router-dom";

import { Button } from "../components/ui.tsx";

export default function NotFound() {
  return (
    <div className="container-page grid min-h-[60vh] place-items-center text-center">
      <div>
        <div className="text-gradient text-7xl font-extrabold">404</div>
        <p className="mt-4 text-lg text-muted">This page could not be found.</p>
        <Link to="/" className="mt-6 inline-block">
          <Button>Back to home</Button>
        </Link>
      </div>
    </div>
  );
}
