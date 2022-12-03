import Table from "react-bootstrap/Table";

import { useApiQuery } from "../../api";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";

export default function Page() {
  const { isLoading, isError, data, error } = useApiQuery<any>("/meta");

  if (isLoading) {
    return <Loader>Loading metadata...</Loader>;
  }

  if (isError) {
    return (
      <ErrorMessage
        title="An error was encountered while loading metadata"
        error={error}
      />
    );
  }

  return (
    <>
      <h2>Site Metadata</h2>

      <Table striped bordered hover>
        <tbody>
          <Entry name="Env" val={data.env} />
          <Entry name="Version" val={data.version} />
        </tbody>
      </Table>
    </>
  );
}

function Entry({
  name,
  val,
  defaultVal = "???",
}: {
  name: string;
  val: any;
  defaultVal?: string;
}) {
  return (
    <tr>
      <th>{name}</th>
      <td>{val ?? defaultVal}</td>
    </tr>
  );
}
