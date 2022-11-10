/* Root Error */

import { Link, useRouteError } from "react-router-dom";

import Container from "react-bootstrap/Container";
import Navbar from "react-bootstrap/Navbar";

export default function Error() {
  const error: any = useRouteError();

  return (
    <>
      <header className="p-4 bg-dark text-light border-bottom shadow-sm">
        <Navbar variant="dark" bg="dark" expand="sm" className="light">
          <Container fluid className="justify-content-between p-0">
            <Link to="/" className="navbar-brand">
              DjangoKit
            </Link>
          </Container>
        </Navbar>
      </header>

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

      <footer className="d-flex align-items-center px-4 py-2 border-top bg-light small">
        <span>&copy; DjangoKit 2022</span>
      </footer>
    </>
  );
}
