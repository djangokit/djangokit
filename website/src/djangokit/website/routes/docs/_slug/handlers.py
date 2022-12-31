from django.shortcuts import get_object_or_404

from ....models import Page


def get(_request, slug):
    page = get_object_or_404(Page, slug=f"doc-{slug}", published=True)
    return {"page": page}
