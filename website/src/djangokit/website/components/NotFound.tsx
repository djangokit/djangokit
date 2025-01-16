import { Link } from "react-router";

export default function NotFound() {
  return (
    <div className="p-3">
      <div className="border border-danger rounded p-3">
        <h2 className="text-danger">Not Found</h2>

        <p className="lead">That page wasn&apos;t found :(</p>

        <p>
          Please re-check the address or visit our <Link to="/">home page</Link>
          .
        </p>
      </div>
    </div>
  );
}
