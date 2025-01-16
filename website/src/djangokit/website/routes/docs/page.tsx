import { useState } from "react";
import { Link } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import FormCheck from "react-bootstrap/FormCheck";
import ListGroup from "react-bootstrap/ListGroup";

import { FaBars, FaEdit } from "react-icons/fa";

import api, { useApiQuery } from "../../api";
import { Page } from "../../models";

import Admonition from "../../components/Admonition";
import Loader from "../../components/Loader";
import ErrorMessage from "../../components/ErrorMessage";

export default function Page() {
  const currentUser = useCurrentUserContext();
  const client = useQueryClient();
  const result = useApiQuery<{ pages: Page[] }>("docs");
  const [dragInfo, setDragInfo] = useState({
    dragging: -1,
    target: -1,
  });
  const { isLoading, isError, data, error } = result;

  const togglePublished = useMutation({
    mutationFn: (page: Page) =>
      api.patch(page.slug, { published: !page.published }),
    onSuccess: () => client.invalidateQueries(["docs"]),
  });

  const reorder = useMutation({
    mutationFn: ({ page, before }: { page: Page; before: Page }) => {
      return api.patch(page.slug, { before: before.id });
    },
    onSuccess: () => client.invalidateQueries(["docs"]),
  });

  return (
    <>
      <p className="lead">Welcome to the DjangoKit documentation!</p>

      <Admonition>
        <p>Documentation is a work in progress.</p>
      </Admonition>

      <p>
        <Link to="get-started">Click here to get started</Link> or click another
        link on the left to jump into a specific topic.
      </p>

      {currentUser.isSuperuser ? (
        <>
          <h3>Admin</h3>

          {isLoading ? <Loader>Loading docs...</Loader> : null}

          {isError ? (
            <ErrorMessage
              title="An error was encountered while loading docs"
              error={error}
            />
          ) : null}

          {!(isLoading || isError) ? (
            <div>
              <ListGroup>
                {data?.pages.map((page, i) => (
                  <ListGroup.Item
                    key={page.id}
                    className={
                      dragInfo.target === i ? "bg-dark text-danger" : ""
                    }
                    draggable
                    // These events apply to the item being dragged
                    onDragStart={() => {
                      setDragInfo({ ...dragInfo, dragging: i });
                    }}
                    onDragEnd={() => {
                      setDragInfo({ dragging: -1, target: -1 });
                    }}
                    // These events apply to items being dragged onto
                    onDragEnter={(event) => {
                      event.preventDefault();
                      setDragInfo({ ...dragInfo, target: i });
                    }}
                    onDragOver={(event) => {
                      event.preventDefault();
                      setDragInfo({ ...dragInfo, target: i });
                    }}
                    onDragLeave={() => {
                      setDragInfo({ dragging: -1, target: -1 });
                    }}
                    onDrop={() => {
                      if (dragInfo.dragging !== dragInfo.target) {
                        reorder.mutate({
                          page: data.pages[dragInfo.dragging],
                          before: data.pages[dragInfo.target],
                        });
                      }
                      setDragInfo({ dragging: -1, target: -1 });
                    }}
                  >
                    <div className="d-flex align-items-center gap-4">
                      <Link
                        to={`/docs/${page.slug.slice(4)}`}
                        className="text-decoration-none"
                      >
                        {page.title}
                      </Link>
                      <span className="flex-fill" />
                      <a
                        title="Edit doc in Django Admin"
                        href={`/$admin/djangokit_website/page/${page.id}/change/`}
                        target="djangokit_admin"
                      >
                        <FaEdit />
                      </a>
                      <span title={page.published ? "Unpublish" : "Publish"}>
                        <FormCheck
                          defaultChecked={page.published}
                          onChange={() => togglePublished.mutate(page)}
                        />
                      </span>
                      <span
                        title="Drag to reorder"
                        style={{ cursor: "pointer" }}
                      >
                        <FaBars />
                      </span>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
              <Admonition>
                <p>
                  The drag and drop reordering is somewhat simplistic. When
                  dropping a page on top of another page, the dropped page will
                  always be inserted <em>before</em> the drop target page.
                </p>
              </Admonition>
            </div>
          ) : null}
        </>
      ) : null}
    </>
  );
}
