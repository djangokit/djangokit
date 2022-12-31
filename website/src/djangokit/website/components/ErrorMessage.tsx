import NotFound from "./NotFound";

interface Props {
  title: string;
  error: {
    message: string;
    statusCode?: number;
  };
}

export default function ErrorMessage({ title, error }: Props) {
  if (error.statusCode === 404) {
    return <NotFound />;
  }

  return (
    <div className="p-4 border border-danger rounded">
      <h2 className="text-danger">⛔️ {title} ⛔️</h2>

      <p className="lead">{error.message}</p>

      {error.statusCode ? (
        <p className="small">Error code: {error.statusCode}</p>
      ) : null}
    </div>
  );
}
