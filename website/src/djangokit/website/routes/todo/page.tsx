import { useState } from "react";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import Button from "react-bootstrap/Button";
import Collapse from "react-bootstrap/Collapse";

import {
  FaCheck,
  FaChevronDown,
  FaChevronUp,
  FaEdit,
  FaPlus,
  FaRegCheckCircle,
  FaRegCircle,
  FaSave,
} from "react-icons/fa";

import api, { useApiQuery } from "../../api";
import { TodoItem, TodoItems } from "../../models";
import Form from "../../components/Form";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import IconButton from "../../components/IconButton";

export default function Page() {
  const currentUser = useCurrentUserContext();

  const [createFormData, setCreateFormData] = useState({ content: "" });
  const [showCompleted, setShowCompleted] = useState(false);

  const client = useQueryClient();
  const { isLoading, isError, data, error } = useApiQuery<TodoItems>("todo");

  const onmutationsuccess = () => {
    client.invalidateQueries({ queryKey: ["todo"] });
  };

  const create = useMutation({
    mutationFn: ({ content }: { content: string }) =>
      api.post("todo", { content }),
    onSuccess: onmutationsuccess,
  });

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

  const todo = data.todo;
  const todoCount = todo.length;
  const completed = data.completed;
  const completedCount = completed.length;

  return (
    <>
      <h2>TODO</h2>

      {currentUser.isSuperuser ? (
        <div className="mb-4">
          <Form
            method="post"
            action="/todo"
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

      {todoCount ? (
        <>
          <h3 className="mt-4 d-flex align-items-center gap-2">
            <FaRegCircle />
            <span>{todoCount}</span>
            <span className="d-none d-sm-inline">
              thing{todoCount === 1 ? "" : "s"}
            </span>
            <span>to do</span>
          </h3>
          <div className="d-flex flex-column gap-2">
            {todo.map((item, i) => (
              <Item key={item.id} item={item} itemNumber={i + 1} />
            ))}
          </div>
        </>
      ) : (
        <div className="alert alert-success">Nothing to do!</div>
      )}

      {completedCount ? (
        <>
          <div>
            <h3 className="mt-4 d-flex align-items-center gap-2">
              <FaRegCheckCircle />
              <span>{completedCount}</span>
              <span className="d-none d-sm-inline">
                thing{completedCount === 1 ? "" : "s"}
              </span>
              <span>done</span>
              <IconButton
                variant="outline-secondary"
                icon={showCompleted ? <FaChevronUp /> : <FaChevronDown />}
                iconPosition="right"
                aria-controls="completed-items"
                aria-expanded={showCompleted}
                className="ms-auto"
                onClick={() => setShowCompleted(!showCompleted)}
              >
                {showCompleted ? "Hide" : "Show"}
                <span className="d-none d-sm-inline"> completed items</span>
              </IconButton>
            </h3>
          </div>
          <Collapse in={showCompleted}>
            <div id="completed-items">
              <div className="d-flex flex-column gap-2">
                {completed.map((item, i) => (
                  <Item key={item.id} item={item} itemNumber={i + 1} />
                ))}
              </div>
            </div>
          </Collapse>
        </>
      ) : null}
    </>
  );
}

function Item({ item, itemNumber }: { item: TodoItem; itemNumber: number }) {
  const currentUser = useCurrentUserContext();

  const [rawContent, setRawContent] = useState(item.rawContent);
  const [editing, setEditing] = useState(false);

  const client = useQueryClient();

  const onMutationSuccess = () => {
    // TODO: Show success indicator
    client.invalidateQueries({ queryKey: ["todo"] });
  };

  const onMutationError = (...args) => {
    // TODO: Show error indicator
    console.error(args);
    client.invalidateQueries({ queryKey: ["todo"] });
  };

  const updateContent = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      api.patch(`todo/${id}`, { content }),
    onSuccess: onMutationSuccess,
    onError: onMutationError,
  });

  const complete = useMutation({
    mutationFn: ({ id }: { id: number }) =>
      api.patch(`todo/${id}`, { completed: true }),
    onSuccess: onMutationSuccess,
    onError: onMutationError,
  });

  const uncomplete = useMutation({
    mutationFn: ({ id }: { id: number }) =>
      api.patch(`todo/${id}`, { completed: false }),
    onSuccess: onMutationSuccess,
    onError: onMutationError,
  });

  const remove = useMutation({
    mutationFn: ({ id }: { id: number }) => api.delete(`todo/${id}`),
    onSuccess: onMutationSuccess,
    onError: onMutationError,
  });

  return (
    <div className="d-flex border rounded">
      <div className="d-flex flex-column align-items-center justify-content-center p-2 text-bg-light border-end">
        {itemNumber}.
      </div>

      <div className="flex-fill align-self-center p-2">
        <ItemContent
          item={item}
          rawContent={rawContent}
          setRawContent={setRawContent}
          editing={editing}
        />
      </div>

      {currentUser.isSuperuser ? (
        <div className="p-2 d-flex flex-column flex-sm-row align-items-center justify-content-center gap-2 text-bg-light border-start">
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
