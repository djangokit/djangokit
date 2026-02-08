from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ....models import Page
from .. import handlers as index_handlers


def get(request: HttpRequest, slug: str):
    kwargs = {}
    if not request.user.is_superuser:
        kwargs["published"] = True
    page = get_object_or_404(Page, slug=f"doc-{slug}", **kwargs)
    pages = index_handlers.get(request)
    return {
        **pages,
        "page": page.serialize(),
    }
