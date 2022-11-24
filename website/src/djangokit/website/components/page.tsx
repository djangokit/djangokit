interface Props {
  isLoading: boolean;
  isError: boolean;
  data: any;
  error: any;
}

export default function page({
  isLoading = false,
  isError = false,
  data = undefined,
  error = undefined,
}: Props) {
  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return (
      <div className="alert alert-danger">
        <h2>An error was encountered while loading this page</h2>

        <div className="lead">
          <span>{error.message}</span>
          {error?.statusCode ? <span> ({error.statusCode})</span> : null}
        </div>
      </div>
    );
  }

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
}
