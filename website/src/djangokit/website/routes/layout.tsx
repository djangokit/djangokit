/* Root Layout */
import { Link, Outlet, useLocation } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import LinkContainer from "react-router-bootstrap/LinkContainer";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";

import { FaBars, FaBookReader, FaGithub } from "react-icons/fa";

import { useApiQuery } from "../api";
import Form from "../components/Form";

function Layout() {
  const currentUser = useCurrentUserContext();
  const location = useLocation();
  const currentPath = location.pathname;
  const redirectPath = encodeURIComponent(currentPath);
  const isLogin = currentPath === "/login";
  const meta = useApiQuery<{ env: string; version: string }>("/meta");

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
              <Nav className="ms-auto">
                <LinkContainer to="/docs">
                  <Nav.Link className="d-flex align-items-center">
                    <FaBookReader />
                    <span className="ms-1">Docs</span>
                  </Nav.Link>
                </LinkContainer>

                <Nav.Link
                  title="DjangoKit Code on GitHub"
                  href="https://github.com/djangokit"
                  className="d-flex align-items-center"
                >
                  <FaGithub />
                  <span className="d-lg-none ms-1">Code</span>
                </Nav.Link>

                {isLogin || currentUser.isAuthenticated ? null : (
                  <Nav.Link as="div">
                    <Link
                      className="btn btn-sm btn-outline-secondary"
                      to={`/login?from=${redirectPath}`}
                    >
                      Log In
                    </Link>
                  </Nav.Link>
                )}
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        {currentUser.isAuthenticated ? (
          <div className="d-flex align-items-center justify-content-end gap-2 small text-muted">
            <div>{currentUser.username}</div>
            <Form method="post" action="/$api/logout">
              <input name="from" type="hidden" value={currentPath} />
              <Button type="submit" size="sm" variant="outline-secondary">
                Log Out
              </Button>
            </Form>
          </div>
        ) : null}
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="d-flex align-items-center justify-content-between px-4 py-2 border-top bg-light small">
        <span>&copy; DjangoKit 2022</span>

        <NavDropdown title={<FaBars />}>
          <LinkContainer to="/todo">
            <NavDropdown.Item>TODO</NavDropdown.Item>
          </LinkContainer>

          <LinkContainer to="/timer">
            <NavDropdown.Item>Timer</NavDropdown.Item>
          </LinkContainer>

          <NavDropdown.Item
            title="Django Admin"
            href="/$admin/"
            target="djangokit_admin"
          >
            Admin
          </NavDropdown.Item>

          {meta.data ? (
            <>
              <NavDropdown.Divider />
              <NavDropdown.Item title="env">
                {meta.data?.env || "development"}
              </NavDropdown.Item>

              {meta.data.version ? (
                <NavDropdown.Item
                  title="version"
                  href={githubUrlForVersion(meta.data.version)}
                >
                  v{meta.data.version ?? "???"}
                </NavDropdown.Item>
              ) : null}

              <LinkContainer to="/meta">
                <NavDropdown.Item title="More metadata">
                  Metadata
                </NavDropdown.Item>
              </LinkContainer>
            </>
          ) : null}
        </NavDropdown>
      </footer>
    </>
  );
}

function githubUrlForVersion(version) {
  return version
    ? `https://github.com/djangokit/djangokit/commit/$version}`
    : "";
}

export default Layout;
