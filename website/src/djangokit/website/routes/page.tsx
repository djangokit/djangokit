/* Home Page */
import { useApi } from "./api";
import { Page } from "./models";

export default function Page() {
  const [data, error] = useApi<Page>("");

  if (data) {
    return (
      <>
        <h2>{data.title}</h2>

        {data.lead ? (
          <div
            className="lead my-4"
            dangerouslySetInnerHTML={{ __html: data.lead }}
          />
        ) : null}

        <div dangerouslySetInnerHTML={{ __html: data.content }} />
      </>
    );
  } else if (error) {
    return (
      <div className="alert alert-danger">
        <p className="lead">
          An error was encountered when fetching the data for this page :(
        </p>

        <p>Status code: {error.statusCode}</p>

        <p>{error.message}</p>
      </div>
    );
  } else {
    return <div>Loading...</div>;
  }
}
