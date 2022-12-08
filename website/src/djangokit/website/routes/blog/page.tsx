import { useApiQuery } from "../../api";
import { BlogPosts } from "../../models";
import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";
import { Link } from "react-router-dom";

export default function Page() {
  const { isLoading, isError, data, error } = useApiQuery<BlogPosts>("blog");

  if (isLoading) {
    return <Loader>Loading blog posts...</Loader>;
  }

  if (isError) {
    return (
      <ErrorMessage
        title="An error was encountered while loading blog posts"
        error={error}
      />
    );
  }

  const posts = data.posts;
  const postCount = posts.length;

  return (
    <>
      {postCount ? (
        posts.map((post, i) => (
          <div key={i}>
            <h3>
              <Link to={post.slug} className="text-decoration-none text-dark">
                {post.title}
              </Link>
            </h3>

            {post.published ? (
              <p className="fst-italic small">
                Published {new Date(post.published).toLocaleString()}
              </p>
            ) : (
              <p className="alert alert-warning">
                This post is a <em>draft</em> and should not be visible to the
                public.
              </p>
            )}

            {post.lead ? (
              <p
                className="lead"
                dangerouslySetInnerHTML={{ __html: post.lead }}
              />
            ) : null}

            <p
              dangerouslySetInnerHTML={{ __html: post.content.slice(0, 100) }}
            />
          </div>
        ))
      ) : (
        <div className="alert alert-warning">No blog posts</div>
      )}
    </>
  );
}
