from django.shortcuts import get_object_or_404

from ...models import Page


def get(_request, slug):
    todo_page = get_object_or_404(Page, slug=slug)
    return todo_page.as_dict()
