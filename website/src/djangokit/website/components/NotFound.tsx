import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="p-4 border border-danger rounded">
      <h2 className="text-danger">⛔️ Not Found ⛔️</h2>

      <p className="lead">That page wasn&apos;t found :(</p>

      <p>
        Please re-check the address or visit our <Link to="/">home page</Link>.
      </p>
    </div>
  );
}
