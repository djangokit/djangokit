import { Link } from "react-router-dom";

export default function Page() {
  return (
    <>
      <p className="lead">Welcome to the DjangoKit documentation!</p>
      <p>
        <Link to="get-started">Click here to get started</Link> or click another
        link on the left to get started.
      </p>
    </>
  );
}
