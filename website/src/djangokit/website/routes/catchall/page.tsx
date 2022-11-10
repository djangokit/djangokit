/* Catchall Page (default 404 page) */

import { Link } from "react-router-dom";

export default function Page() {
  return (
    <div className="p-4 border border-danger rounded">
      <h1 className="text-danger">⛔️ Not Found</h1>

      <p className="lead">That page wasn&apos;t found :(</p>

      <p>
        Please re-check the address or visit our <Link to="/">home page</Link>.
      </p>
    </div>
  );
}
