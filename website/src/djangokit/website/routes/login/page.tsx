import { useSearchParams } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Stack from "react-bootstrap/Stack";

declare const CsrfTokenField;

export default function Page() {
  const [params, _] = useSearchParams();
  const from = params.get("from") ?? "/";

  return (
    <Form method="post" action="/$api/login" className="container-lg">
      <CsrfTokenField />
      <input name="from" type="hidden" value={from} />
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
