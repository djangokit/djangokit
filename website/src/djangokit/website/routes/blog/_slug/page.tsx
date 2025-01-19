import { useApiQuery } from "../../../api";
import { BlogPost } from "../../../models";
import { useParams } from "react-router-dom";
import Loader from "../../../components/Loader";
import ErrorMessage from "../../../components/ErrorMessage";

export default function Page() {
  const { slug } = useParams();

  const {
    isLoading,
    isError,
    data: post,
    error,
  } = useApiQuery<BlogPost>(`blog/${slug}`);

  if (isLoading) {
    return <Loader>Loading blog post...</Loader>;
  }

  if (isError) {
    return <ErrorMessage title="Could not load that post :(" error={error} />;
  }

  return (
    <div className="p-3">
      <h2>{post.title}</h2>

      <p className="fst-italic small">
        by {post.author.username}
        {post.published ? (
          <span>
            {" "}
            &middot; published {new Date(post.published).toLocaleString()}
          </span>
        ) : null}
      </p>

      {!post.published ? (
        <p className="alert alert-warning">
          This post is a <em>draft</em> and should not be visible to the public.
        </p>
      ) : null}

      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </div>
  );
}
