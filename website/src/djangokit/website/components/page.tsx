import ErrorMessage from "./ErrorMessage";
import Loader from "./Loader";

interface Props {
  isLoading: boolean;
  isError: boolean;
  data: any;
  error: any;
}

export default function Page({
  isLoading = false,
  isError = false,
  data = undefined,
  error = undefined,
}: Props) {
  if (isLoading) {
    return <Loader>Loading page...</Loader>;
  }

  if (isError) {
    return (
      <ErrorMessage
        title="An error was encountered while loading this page"
        error={error}
      />
    );
  }

  return (
    <div>
      <h2>{data.title}</h2>

      {data.lead ? (
        <div
          className="lead my-4"
          dangerouslySetInnerHTML={{ __html: data.lead }}
        />
      ) : null}

      <div dangerouslySetInnerHTML={{ __html: data.content }} />
    </div>
  );
}
