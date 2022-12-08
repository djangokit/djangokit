from django.shortcuts import get_list_or_404

from ...models import Page


def get(request):
    prefix = "doc-"
    if request.user.is_superuser:
        pages = get_list_or_404(Page, slug__startswith=prefix)
    else:
        pages = get_list_or_404(Page, slug__startswith=prefix, published=True)
    return {"pages": pages}
