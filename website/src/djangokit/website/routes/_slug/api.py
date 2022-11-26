from django.shortcuts import get_object_or_404

from ...models import Page, PageSchema


def get(_request, slug):
    page = get_object_or_404(Page, slug=slug)
    return PageSchema().dump(page)
