/* Root Layout */
import { Link, Outlet } from "react-router-dom";
import Container from "react-bootstrap/Container";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import LinkContainer from "react-router-bootstrap/LinkContainer";

function Layout() {
  return (
    <>
      <header className="p-4 bg-light border-bottom shadow-sm">
        <Navbar bg="light" expand="lg">
          <Container fluid className="p-0">
            <Link to="/" className="navbar-brand">
              DjangoKit
            </Link>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <LinkContainer to="/docs">
                  <Nav.Link>Docs</Nav.Link>
                </LinkContainer>
                <LinkContainer to="/todos">
                  <Nav.Link>TODO</Nav.Link>
                </LinkContainer>
                <Nav.Link href="https://github.com/djangokit">Code</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="d-flex align-items-center px-4 py-2 border-top bg-light small">
        <span className="flex-fill">&copy; DjangoKit 2022</span>
        <a
          href="/$admin/"
          target="djangokit_admin"
          className="btn btn-sm btn-outline-secondary"
        >
          Admin
        </a>
      </footer>
    </>
  );
}

export default Layout;
