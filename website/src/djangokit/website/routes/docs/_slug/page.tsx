import { useParams } from "react-router-dom";

import { usePageQuery } from "../../../api";
import ErrorMessage from "../../../components/ErrorMessage";
import Loader from "../../../components/Loader";

export default function Page() {
  const { slug } = useParams();
  const { isLoading, isError, data, error } = usePageQuery(`doc-${slug}`);

  if (isLoading) {
    return <Loader>Loading doc {slug}...</Loader>;
  }

  if (isError) {
    return <ErrorMessage title="Could not load doc {slug} :(" error={error} />;
  }

  return (
    <>
      <h2>{data.title}</h2>
      {data.lead ? (
        <div dangerouslySetInnerHTML={{ __html: data.lead }} className="mb-4" />
      ) : null}
      <div dangerouslySetInnerHTML={{ __html: data.content }} />
    </>
  );
}
