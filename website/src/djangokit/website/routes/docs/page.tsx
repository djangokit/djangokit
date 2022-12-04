import { Link } from "react-router-dom";

export default function Page() {
  return (
    <>
      <p className="lead">Welcome to the DjangoKit documentation!</p>
      <div className="admonition note">
        <p className="admonition-title">Note</p>
        <p>Documentation is a work in progress.</p>
      </div>
      <p>
        <Link to="get-started">Click here to get started</Link> or click another
        link on the left to jump into a specific topic.
      </p>
    </>
  );
}
