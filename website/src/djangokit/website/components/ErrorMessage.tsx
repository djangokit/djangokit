interface Props {
  title: string;
  error: {
    message: string;
    statusCode?: number;
  };
}

export default function ErrorMessage({ title, error }: Props) {
  return (
    <div className="alert alert-danger">
      <h2>{title}</h2>
      <div className="lead">
        <span>{error.message}</span>
        {error.statusCode ? <span> ({error.statusCode})</span> : null}
      </div>
    </div>
  );
}
