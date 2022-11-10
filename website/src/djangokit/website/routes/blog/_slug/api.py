from ....models import BlogPost


def get(request, slug):
    kwargs = {"slug": slug}
    if not request.user.is_superuser:
        kwargs["published__isnull"] = False
    try:
        return BlogPost.objects.select_related("author").get(**kwargs)
    except BlogPost.DoesNotExist:
        return 404, f"Blog post not found: {slug}"
