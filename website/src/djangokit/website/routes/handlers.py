from django.shortcuts import get_object_or_404

from ..models import Page


def get(_request):
    page = get_object_or_404(Page, slug="home")
    return {"page": page.serialize()}
