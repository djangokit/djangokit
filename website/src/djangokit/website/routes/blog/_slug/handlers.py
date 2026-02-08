from ....models import BlogPost


def get(request, slug):
    kwargs = {"slug": slug}
    if not request.user.is_superuser:
        kwargs["published__isnull"] = False
    try:
        post: BlogPost = BlogPost.objects.select_related("author").get(**kwargs)
        return post.serialize()
    except BlogPost.DoesNotExist:
        return 404, f"Blog post not found: {slug}"
