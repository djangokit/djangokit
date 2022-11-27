import { Outlet, useLocation } from "react-router-dom";

import LinkContainer from "react-router-bootstrap/LinkContainer";
import Nav from "react-bootstrap/Nav";

import { useApiQuery } from "../../api";
import { Page } from "../../models";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";

export default function Layout() {
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
    <div className="d-flex flex-column flex-md-row gap-4 h-100">
      <Nav
        variant="pills"
        className="flex-row flex-md-column"
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

      <div className="flex-fill">
        <Outlet />
      </div>
    </div>
  );
}
