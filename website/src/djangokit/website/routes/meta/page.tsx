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

  const settings = data.settings ?? {};
  const djangokitSettings = settings.DJANGOKIT ?? {};

  return (
    <>
      <h2>Site Metadata</h2>

      <Table striped bordered hover>
        <tbody>
          <Entry name="env" val={data.env} />
          <Entry name="version" val={data.version} />

          {Object.entries(settings).map(([name, val], i) =>
            name === "DJANGOKIT" ? null : (
              <Entry key={i} name={name} val={val} />
            )
          )}

          {Object.entries(djangokitSettings).map(([name, val], i) => (
            <Entry key={i} name={`DJANGOKIT.${name}`} val={val} />
          ))}
        </tbody>
      </Table>
    </>
  );
}

function Entry({
  name,
  val,
  defaultVal,
}: {
  name: string;
  val: any;
  defaultVal?: string;
}) {
  return (
    <tr>
      <th>{name}</th>
      <td>{convertVal(val, defaultVal)}</td>
    </tr>
  );
}

function convertVal(val: any, defaultVal?: string): string {
  if (val === undefined) {
    return defaultVal ?? "undefined";
  }
  return JSON.stringify(val, undefined, 1);
}
