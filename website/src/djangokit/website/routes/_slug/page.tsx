import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "../api";

export default function Page() {
  const { slug } = useParams();

  const { isLoading, isError, data, error } = useQuery({
    queryKey: [`page-${slug}`],
    queryFn: async () => await apiFetch(slug ?? "404"),
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return (
      <div className="alert alert-danger">
        <p className="lead">
          An error was encountered while loading this page :(
        </p>

        <p>{error.message}</p>
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
