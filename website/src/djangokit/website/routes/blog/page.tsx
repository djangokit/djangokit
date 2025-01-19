import { Link } from "react-router-dom";
import { FaEdit } from "react-icons/fa";

import { useApiQuery } from "../../api";
import { BlogPosts } from "../../models";

import ErrorMessage from "../../components/ErrorMessage";
import Loader from "../../components/Loader";

export default function Page() {
  const currentUser = useCurrentUserContext();
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
    <div className="p-3">
      <h2>DjangoKit Blog</h2>

      <hr />

      {postCount ? (
        posts.map((post, i) => (
          <div key={i}>
            <h3 className="d-flex align-items-center gap-2">
              <span>{post.title}</span>
              <Link
                to={post.slug}
                title={`Link to blog post: ${post.title}`}
                className="text-decoration-none"
              >
                🔗
              </Link>
              {currentUser.isSuperuser ? (
                <a
                  title="Edit post in Django Admin"
                  href={`/$admin/djangokit_website/blogpost/${post.id}/change/`}
                  target="djangokit_admin"
                  className="ms-auto"
                >
                  <FaEdit />
                </a>
              ) : null}
            </h3>

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
                This post is a <em>draft</em> and should not be visible to the
                public.
              </p>
            ) : null}

            {post.lead ? (
              <p
                className="lead"
                dangerouslySetInnerHTML={{ __html: post.lead }}
              />
            ) : null}

            <p dangerouslySetInnerHTML={{ __html: post.blurb }} />

            <p className="fst-italic">
              <Link to={post.slug} title="Read this post">
                Read more
              </Link>
            </p>

            <hr />
          </div>
        ))
      ) : (
        <div className="alert alert-warning">No blog posts</div>
      )}
    </div>
  );
}
