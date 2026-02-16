from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from djangokit.core import handler

from .... import auth
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


@handler("post")
@auth.require_staff
def up(request: HttpRequest, slug: str):
    result = 303, request.META.get("HTTP_REFERER") or "/"
    page_id = int(slug)
    pages = list(Page.objects.order_by("order").all())
    found_page = False

    for i, page in enumerate(pages):
        order = i + 1
        if page.id == page_id:
            if order == 1:
                return result
            page.order = order - 1
            pages[i - 1].order = order
            found_page = True
        else:
            page.order = order

    if not found_page:
        return 404

    Page.objects.bulk_update(pages, fields=["order"])
    return result


@handler("post")
@auth.require_staff
def down(request: HttpRequest, slug: str):
    result = 303, request.META.get("HTTP_REFERER") or "/"
    page_id = int(slug)
    pages = list(Page.objects.order_by("order").all())
    found_page = False
    skip_next = False

    for i, page in enumerate(pages):
        order = i + 1
        if page.id == page_id:
            if order == len(pages):
                return result
            page.order = order + 1
            pages[i + 1].order = order
            found_page = True
            skip_next = True
        elif skip_next:
            skip_next = False
        else:
            page.order = order

    if not found_page:
        return 404

    Page.objects.bulk_update(pages, fields=["order"])
    return result
