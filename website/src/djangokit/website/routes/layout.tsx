/* Root Layout */
import { Link, Outlet, useLocation } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import LinkContainer from "react-router-bootstrap/LinkContainer";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";

import { FaBars, FaBookReader, FaGithub, FaRocket } from "react-icons/fa";

import { useApiQuery } from "../api";

import Form from "../components/Form";
import IconButton from "../components/IconButton";

export default function Layout() {
  const currentUser = useCurrentUserContext();
  const location = useLocation();
  const currentPath = location.pathname;
  const redirectPath = encodeURIComponent(currentPath);
  const isLogin = currentPath === "/login";
  const meta = useApiQuery<{ env: string; version: string }>("/meta");

  return (
    <>
      <header className="border-bottom shadow-sm">
        <div className="d-flex align-items-center justify-content-between p-3 bg-dark text-light">
          <Link to="/" className="navbar-brand">
            DjangoKit
          </Link>

          {currentPath.startsWith("/docs") ? null : (
            <LinkContainer to="/docs/get-started">
              <IconButton size="sm" variant="outline-info" icon={<FaRocket />}>
                <span className="d-inline d-sm-none">Start</span>
                <span className="d-none d-sm-inline">Get Started</span>
              </IconButton>
            </LinkContainer>
          )}

          {currentUser.isAuthenticated ? (
            <div className="d-flex align-items-center gap-2">
              <div>{currentUser.username}</div>
              <Form method="post" action="/$api/logout">
                <input name="next" type="hidden" value={currentPath} />
                <Button type="submit" size="sm" variant="outline-secondary">
                  Log Out
                </Button>
              </Form>
            </div>
          ) : null}

          {currentUser.isAuthenticated || isLogin ? null : (
            <Link
              className="btn btn-sm btn-outline-secondary"
              to={`/login?next=${redirectPath}`}
            >
              Log In
            </Link>
          )}
        </div>

        <Navbar variant="dark" bg="dark" expand="sm" collapseOnSelect>
          <Container fluid className="justify-content-end">
            <Navbar.Toggle aria-controls="main-navbar" />
            <Navbar.Collapse id="main-navbar" className="justify-content-end">
              <Nav className="align-items-end">
                <LinkContainer to="/about">
                  <Nav.Link>About</Nav.Link>
                </LinkContainer>

                <LinkContainer to="/ideas">
                  <Nav.Link>Ideas</Nav.Link>
                </LinkContainer>

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
                  <span className="ms-1">Code</span>
                </Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>
      </header>

      <main className="p-4">
        <Outlet />
      </main>

      <footer className="d-flex align-items-center justify-content-between px-4 py-2 border-top bg-light small">
        <span>&copy; 2022 DjangoKit.org</span>

        <NavDropdown title={<FaBars />}>
          <LinkContainer to="/blog">
            <NavDropdown.Item>Blog</NavDropdown.Item>
          </LinkContainer>

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
