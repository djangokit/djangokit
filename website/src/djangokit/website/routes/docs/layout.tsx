import { Outlet, useLocation } from "react-router-dom";

import LinkContainer from "react-router-bootstrap/LinkContainer";
import Nav from "react-bootstrap/Nav";

import { useApiQuery } from "../../api";
import { Page } from "../../models";

export default function Layout() {
  const location = useLocation();
  const result = useApiQuery<{ pages: Page[] }>("docs");
  const { isLoading, isError, data, error } = result;

  if (isLoading) {
    return <div>Loading docs...</div>;
  }

  if (isError) {
    return (
      <div className="alert alert-danger">
        <h2>Could not load the docs :(</h2>
        <div className="lead">
          <span>{error.message}</span>
          {error?.statusCode ? <span> ({error.statusCode})</span> : null}
        </div>
      </div>
    );
  }

  return (
    <div className="d-flex">
      <div className="w-25 gap-4 pe-4 border-end">
        <Nav
          variant="pills"
          className="flex-column"
          activeKey={location.pathname}
        >
          {data.pages.map((page) => (
            <Nav.Item key={page.id}>
              <LinkContainer to={`/docs/${page.slug.slice(4)}`}>
                <Nav.Link>{page.title}</Nav.Link>
              </LinkContainer>
            </Nav.Item>
          ))}
        </Nav>
      </div>

      <div className="ps-4 w-75">
        <Outlet />
      </div>
    </div>
  );
}
