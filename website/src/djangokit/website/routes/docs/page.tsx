import { Link } from "react-router-dom";
import ListGroup from "react-bootstrap/ListGroup";
import { FaBars } from "react-icons/fa";

import api, { useApiQuery } from "../../api";
import { Page } from "../../models";
import Loader from "../../components/Loader";
import ErrorMessage from "../../components/ErrorMessage";
import FormCheck from "react-bootstrap/FormCheck";
import { useMutation, useQueryClient } from "@tanstack/react-query";

export default function Page() {
  const currentUser = useCurrentUserContext();
  const client = useQueryClient();
  const result = useApiQuery<{ pages: Page[] }>("docs");
  const { isLoading, isError, data, error } = result;

  const togglePublished = useMutation({
    mutationFn: (page: Page) =>
      api.patch(`${page.slug}`, { published: !page.published }),
    onSuccess: () => client.invalidateQueries(["docs"]),
  });

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

      {currentUser.isSuperuser ? (
        <>
          {isLoading ? <Loader>Loading docs...</Loader> : null}

          {isError ? (
            <ErrorMessage
              title="An error was encountered while loading docs"
              error={error}
            />
          ) : null}

          {!(isLoading || isError) ? (
            <ListGroup>
              {data?.pages.map((page) => (
                <ListGroup.Item key={page.id}>
                  <div className="d-flex align-items-center gap-2">
                    <span>{page.order}.</span>
                    <span>{page.title}</span>
                    <span className="flex-fill" />
                    <FormCheck
                      defaultChecked={page.published}
                      onChange={(event) => togglePublished.mutate(page)}
                    />
                    <span>
                      <FaBars />
                    </span>
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          ) : null}
        </>
      ) : null}
    </>
  );
}
