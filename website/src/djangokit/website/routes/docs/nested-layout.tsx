import { Outlet, useLocation } from "react-router-dom";

import LinkContainer from "react-router-bootstrap/LinkContainer";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";

import { useApiQuery } from "../../api";
import { Page } from "../../models";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";

export default function NestedLayout() {
  const location = useLocation();
  const result = useApiQuery<{ pages: Page[] }>("docs");
  const { isLoading, isError, data, error } = result;

  if (isLoading) {
    return <Loader>Loading docs...</Loader>;
  }

  if (isError) {
    return <ErrorMessage title="Could not load the docs :(" error={error} />;
  }

  return (
    <div className="d-flex flex-column flex-md-row flex-fill">
      <Navbar
        bg="dark"
        variant="dark"
        expand="md"
        collapseOnSelect
        className="flex-md-column p-3 p-md-4"
        style={{ minWidth: "192px" }}
      >
        <Navbar.Toggle aria-controls="nav-docs" className="d-md-none w-100">
          <div className="d-flex align-items-center gap-2">
            <span className="navbar-toggler-icon"></span>
            <span>Docs Menu</span>
          </div>
        </Navbar.Toggle>
        <Navbar.Collapse id="nav-docs" className="flex-column">
          <Nav className="flex-column" activeKey={location.pathname}>
            {data.pages.map((page) => (
              <Nav.Item key={page.id}>
                <LinkContainer to={`/docs/${page.slug.slice(4)}`}>
                  <Nav.Link
                    className={`text-decoration-underline ${
                      page.published
                        ? ""
                        : "text-danger text-decoration-line-through"
                    }`}
                    title={`Doc - ${page.title}${
                      page.published ? "" : " (unpublished)"
                    }`}
                  >
                    {page.title}
                  </Nav.Link>
                </LinkContainer>
              </Nav.Item>
            ))}
          </Nav>
        </Navbar.Collapse>
      </Navbar>

      <div className="p-3 flex-fill">
        <Outlet />
      </div>
    </div>
  );
}
