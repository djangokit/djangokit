import { useState } from "react";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import Button from "react-bootstrap/Button";
import Card from "react-bootstrap/Card";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";

import api, { useApiQuery } from "../../api";
import { TodoItems } from "../../models";

export default function Page() {
  const client = useQueryClient();

  const { isLoading, isError, data, error } = useApiQuery<TodoItems>("todos");

  const [createFormData, setCreateFormData] = useState({ content: "" });

  const onMutationSuccess = () => {
    client.invalidateQueries({ queryKey: ["todos"] });
  };

  const create = useMutation({
    mutationFn: ({ content }: { content: string }) =>
      api.post("todos", { content }),
    onSuccess: onMutationSuccess,
  });

  const updateContent = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      api.patch(`todos/${id}`, { content }),
    onSuccess: onMutationSuccess,
  });

  const complete = useMutation({
    mutationFn: ({ id }: { id: number }) =>
      api.patch(`todos/${id}`, { completed: true }),
    onSuccess: onMutationSuccess,
  });

  const uncomplete = useMutation({
    mutationFn: ({ id }: { id: number }) =>
      api.patch(`todos/${id}`, { completed: false }),
    onSuccess: onMutationSuccess,
  });

  const remove = useMutation({
    mutationFn: ({ id }: { id: number }) => api.delete(`todos/${id}`),
    onSuccess: onMutationSuccess,
  });

  if (isLoading) {
    return <div>Loading TODO items...</div>;
  }

  if (isError) {
    return (
      <div className="alert alert-danger">
        <h2>An error was encountered while loading TODO items</h2>

        <div className="lead">
          <span>{error.message}</span>
          {error?.statusCode ? <span> ({error.statusCode})</span> : null}
        </div>
      </div>
    );
  }

  return (
    <>
      <h2>TODO</h2>

      <Form
        className="mb-4"
        onSubmit={(event) => {
          event.preventDefault();
          create.mutate(createFormData);
          setCreateFormData({ content: "" });
        }}
      >
        <Form.Control
          as="textarea"
          required
          placeholder="Do stuff"
          className="mb-2"
          value={createFormData.content}
          onChange={(event) =>
            setCreateFormData({ content: event.target.value })
          }
        ></Form.Control>

        <div className="d-flex align-items-center justify-content-center">
          <Button type="submit">Add</Button>
        </div>
      </Form>

      <hr />

      {data.items.length ? (
        data.items.map((item) => (
          <Card key={item.id} className="mb-4">
            <Card.Body>
              {item.completed ? (
                <Card.Text className="text-muted">
                  <del dangerouslySetInnerHTML={{ __html: item.content }} />
                </Card.Text>
              ) : (
                <Form.Control
                  as="textarea"
                  defaultValue={item.rawContent}
                  onBlur={(event) =>
                    updateContent.mutate({
                      id: item.id,
                      content: event.target.value,
                    })
                  }
                ></Form.Control>
              )}
            </Card.Body>

            <Card.Footer className="small fw-light fst-italic">
              <Row
                xs={1}
                md={2}
                className="align-items-center justify-content-between"
              >
                <Col className="text-center text-md-start mb-2 mb-md-0">
                  {item.completed ? (
                    <>
                      Completed {new Date(item.completed).toLocaleDateString()}{" "}
                      at {new Date(item.completed).toLocaleTimeString()}
                    </>
                  ) : (
                    <>
                      Created {new Date(item.created).toLocaleDateString()}{" "}
                      {new Date(item.created).toLocaleTimeString()}
                    </>
                  )}
                </Col>

                <Col className="d-flex justify-content-end">
                  {item.completed ? (
                    <Button
                      size="sm"
                      variant="warning"
                      onClick={() => uncomplete.mutate({ id: item.id })}
                    >
                      Uncomplete
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline-success"
                      onClick={() => complete.mutate({ id: item.id })}
                    >
                      Complete
                    </Button>
                  )}

                  <Button
                    size="sm"
                    variant="danger"
                    className="ms-2"
                    onClick={() => remove.mutate({ id: item.id })}
                  >
                    Delete
                  </Button>
                </Col>
              </Row>
            </Card.Footer>
          </Card>
        ))
      ) : (
        <div>No todo items!</div>
      )}
    </>
  );
}
