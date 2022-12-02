import { useState } from "react";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import Button from "react-bootstrap/Button";

import { FaCheck, FaEdit, FaPlus, FaSave } from "react-icons/all";

import api, { useApiQuery } from "../../api";
import { TodoItem, TodoItems } from "../../models";
import Form from "../../components/Form";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";

export default function Page() {
  const currentUser = useCurrentUserContext();
  const { isLoading, isError, data, error } = useApiQuery<TodoItems>("todo");

  const client = useQueryClient();

  const onmutationsuccess = () => {
    client.invalidateQueries({ queryKey: ["todo"] });
  };

  const create = useMutation({
    mutationFn: ({ content }: { content: string }) =>
      api.post("todo", { content }),
    onSuccess: onmutationsuccess,
  });

  const [createFormData, setCreateFormData] = useState({ content: "" });

  if (isLoading) {
    return <Loader>Loading TODO items...</Loader>;
  }

  if (isError) {
    return (
      <ErrorMessage
        title="An error was encountered while loading TODO items"
        error={error}
      />
    );
  }

  const items = data.items;
  const numItems = items.length;

  return (
    <>
      <h2>TODO</h2>

      {currentUser.isSuperuser ? (
        <div className="mb-4">
          <Form
            method="post"
            action="/$api/todo"
            className="d-flex flex-row gap-2 mb-1"
            onSubmit={(event) => {
              event.preventDefault();
              create.mutate(createFormData);
              setCreateFormData({ content: "" });
            }}
          >
            <Form.Control
              as="textarea"
              name="content"
              required
              placeholder="Do all the things and then all the stuff..."
              className="flex-fill"
              value={createFormData.content}
              onChange={(event) =>
                setCreateFormData({ content: event.target.value })
              }
            ></Form.Control>

            <div className="d-flex justify-content-center">
              <Button type="submit" disabled={!createFormData.content}>
                <FaPlus />
              </Button>
            </div>
          </Form>

          <div className="text-muted small">NOTE: You can use Markdown</div>
        </div>
      ) : null}

      {numItems ? (
        <>
          <h3>
            {numItems} thing{numItems === 1 ? "" : "s"} to do
          </h3>
          <div className="d-flex flex-column gap-4">
            {items.map((item, i) => (
              <Item key={item.id} item={item} cardinal={i + 1} />
            ))}
          </div>
        </>
      ) : (
        <div className="alert alert-success">Nothing to do!</div>
      )}
    </>
  );
}

function Item({ item, cardinal }: { item: TodoItem; cardinal: number }) {
  const currentUser = useCurrentUserContext();

  const [rawContent, setRawContent] = useState(item.rawContent);
  const [editing, setEditing] = useState(false);

  const client = useQueryClient();

  const onmutationsuccess = () => {
    client.invalidateQueries({ queryKey: ["todo"] });
  };

  const updateContent = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      api.patch(`todo/${id}`, { content }),
    onSuccess: onmutationsuccess,
  });

  const complete = useMutation({
    mutationFn: ({ id }: { id: number }) =>
      api.patch(`todo/${id}`, { completed: true }),
    onSuccess: onmutationsuccess,
  });

  const uncomplete = useMutation({
    mutationFn: ({ id }: { id: number }) =>
      api.patch(`todo/${id}`, { completed: false }),
    onSuccess: onmutationsuccess,
  });

  const remove = useMutation({
    mutationFn: ({ id }: { id: number }) => api.delete(`todo/${id}`),
    onSuccess: onmutationsuccess,
  });

  return (
    <div className="d-flex border rounded">
      <div className="d-flex flex-column align-items-center justify-content-center p-2 text-bg-light border-end">
        {cardinal}.
      </div>

      <div className="flex-fill p-2 border-end">
        <ItemContent
          item={item}
          rawContent={rawContent}
          setRawContent={setRawContent}
          editing={editing}
        />
      </div>

      {currentUser.isSuperuser ? (
        <div className="p-2 d-flex flex-column justify-content-center gap-2 text-bg-light">
          <ItemControls
            item={item}
            rawContent={rawContent}
            setRawContent={setRawContent}
            editing={editing}
            setEditing={setEditing}
            updateContent={updateContent}
            complete={complete}
            uncomplete={uncomplete}
            remove={remove}
          />
        </div>
      ) : null}
    </div>
  );
}

function ItemContent({
  item,
  rawContent,
  setRawContent,
  editing,
}: {
  item: TodoItem;
  rawContent: string;
  setRawContent: any;
  editing: boolean;
}) {
  if (item.completed) {
    return (
      <del
        className="text-muted"
        title={`Completed ${new Date(item.completed).toLocaleString()}`}
        dangerouslySetInnerHTML={{ __html: item.content }}
      />
    );
  }

  if (editing) {
    return (
      <Form.Control
        as="textarea"
        value={rawContent}
        style={{ height: "16rem" }}
        onChange={(event) => setRawContent(event.target.value)}
      />
    );
  }

  return (
    <div
      title={`Created ${new Date(item.created).toLocaleString()}`}
      dangerouslySetInnerHTML={{ __html: item.content }}
    />
  );
}

function ItemControls({
  item,
  rawContent,
  setRawContent,
  editing,
  setEditing,
  updateContent,
  complete,
  uncomplete,
  remove,
}: {
  item: TodoItem;
  rawContent: string;
  setRawContent: any;
  editing: boolean;
  setEditing: any;
  updateContent: any;
  complete: any;
  uncomplete: any;
  remove: any;
}) {
  if (editing) {
    return (
      <>
        <Button
          size="sm"
          variant="outline-primary"
          title="Save changes"
          onClick={() => {
            updateContent.mutate({ id: item.id, content: rawContent });
            setEditing(false);
          }}
        >
          <FaSave />
        </Button>

        <Button
          size="sm"
          variant="outline-secondary"
          title="Discard changes / cancel editing"
          onClick={() => {
            setRawContent(item.rawContent);
            setEditing(false);
          }}
        >
          &times;
        </Button>
      </>
    );
  }

  return (
    <>
      {item.completed ? (
        <Button
          size="sm"
          variant="outline-warning"
          title="Mark as not completed"
          onClick={() => uncomplete.mutate({ id: item.id })}
        >
          <FaCheck />
        </Button>
      ) : (
        <>
          <Button
            size="sm"
            variant="outline-success"
            title="Mark as completed"
            onClick={() => complete.mutate({ id: item.id })}
          >
            <FaCheck />
          </Button>

          <Button
            size="sm"
            variant="outline-info"
            title="Edit"
            onClick={() => setEditing(true)}
          >
            <FaEdit />
          </Button>
        </>
      )}

      <Button
        size="sm"
        variant="outline-danger"
        onClick={() =>
          confirm("Delete TODO item?") && remove.mutate({ id: item.id })
        }
        title="Delete!"
      >
        &times;
      </Button>
    </>
  );
}
