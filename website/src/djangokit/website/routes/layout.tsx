/* Root Layout */
import { Link, Outlet } from "react-router-dom";
import { Container, Nav, Navbar } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";

function Layout() {
  return (
    <>
      <header className="p-4 bg-light border-bottom">
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
                <LinkContainer to="/todo">
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

      <footer className="d-flex fixed-bottom p-4 border-top bg-light">
        <span className="flex-fill">&copy; DjangoKit 2022</span>
        <a href="/$admin" target="djangokit_admin">
          Admin
        </a>
      </footer>
    </>
  );
}

export default Layout;
