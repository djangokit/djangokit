import { useSearchParams } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Stack from "react-bootstrap/Stack";

import Form from "../../components/Form";

export default function Page() {
  const [params] = useSearchParams();
  const next = params.get("next") ?? "/";

  return (
    <Form method="post" action="/login" className="container-lg p-3">
      <input name="next" type="hidden" value={next} />
      <Stack gap={4}>
        <h2>Log In</h2>

        <Form.Group>
          <Form.Label>Username</Form.Label>
          <Form.Control name="username" type="text" />
        </Form.Group>

        <Form.Group>
          <Form.Label>Password</Form.Label>
          <Form.Control name="password" type="password" />
        </Form.Group>

        <Button variant="primary" type="submit">
          Log In
        </Button>
      </Stack>
    </Form>
  );
}
