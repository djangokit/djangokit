"""API for individual todo items."""
import json

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from ....models import TodoItem


def get(_request, id):
    item = get_object_or_404(TodoItem, id=id)
    return item.as_dict()


def delete(_request, id):
    item = get_object_or_404(TodoItem, id=id)
    item.delete()


def patch(request, id):
    data = json.loads(request.body)
    item = get_object_or_404(TodoItem, id=id)
    save = False

    if "content" in data:
        item.content = data["content"]
        save = True

    if "completed" in data:
        completed = data["completed"]
        item.completed = now() if completed else None
        save = True

    if save:
        item.save()
    else:
        return HttpResponseBadRequest("No known todo item fields were specified")
