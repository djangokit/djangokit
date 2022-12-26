import { useParams } from "react-router-dom";
import { FaEdit } from "react-icons/fa";

import { usePageQuery } from "../../../api";
import ErrorMessage from "../../../components/ErrorMessage";
import Loader from "../../../components/Loader";

export default function Page() {
  const currentUser = useCurrentUserContext();
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

      {currentUser.isSuperuser ? (
        <a
          title="Edit doc in Django Admin"
          href={`/$admin/djangokit_website/page/${data.id}/change/`}
          target="djangokit_admin"
          className="d-flex align-items-center gap-2"
        >
          <FaEdit />
          Edit Page
        </a>
      ) : null}

      {data.lead ? (
        <div
          dangerouslySetInnerHTML={{ __html: data.lead }}
          className="lead mb-4"
        />
      ) : null}
      <div dangerouslySetInnerHTML={{ __html: data.content }} />
    </>
  );
}
