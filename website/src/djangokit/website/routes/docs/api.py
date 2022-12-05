from django.shortcuts import get_list_or_404

from ...models import Page


def get(_request):
    pages = get_list_or_404(Page, slug__startswith="doc-", published=True)
    return {"pages": pages}
