from django.http import Http404
from django.shortcuts import get_object_or_404

from ...models import Page


def get_object_or_404_json(*args, **kwargs):
    try:
        get_object_or_404(*args, **kwargs)
    except Http404 as exc:
        raise Http404()


def get(_request, slug):
    todo_page = get_object_or_404(Page, slug=slug)
    return todo_page.as_dict()
