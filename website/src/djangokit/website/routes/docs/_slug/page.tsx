import { useParams } from "react-router-dom";

import { usePageQuery } from "../../../api";

export default function Page() {
  const { slug } = useParams();
  const { isLoading, isError, data, error } = usePageQuery(`doc-${slug}`);

  if (isLoading) {
    return <div>Loading doc {slug}...</div>;
  }

  if (isError) {
    return (
      <div className="alert alert-danger">
        <h2>Could not load doc {slug} :(</h2>
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
      <div dangerouslySetInnerHTML={{ __html: data.content }} />
    </>
  );
}
