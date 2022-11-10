/* Root Error */

import { Link, useRouteError } from "react-router-dom";

export default function Error() {
  const error: any = useRouteError();

  return (
    <>
      <main className="p-4">
        <h2>⛔️ Error</h2>

        <p className="lead">
          An error was encountered while attempting to load this page.
        </p>

        <p>
          Please return to the previous page using your browser&apos;s back
          button or the <Link to="/">home page</Link>.
        </p>

        <hr />

        <p className="small">Technical info: {error.toString()}</p>
      </main>
    </>
  );
}
