from ...models import Page


def get(request):
    """Get page data for docs index.

    Only the necessary fields are included.

    """
    args = {"slug__startswith": "doc-"}
    fields = ["id", "slug", "title", "published"]
    if not request.user.is_superuser:
        args["published"] = True
    pages = Page.objects.filter(**args).values(*fields)
    return {"pages": pages}
