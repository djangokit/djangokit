"""API for todo item collection."""
import json

from django.http import HttpResponseBadRequest

from djangokit.website import auth
from djangokit.website.models import TodoItem


def get(_request):
    """Get all todo items."""
    items = TodoItem.objects.all().order_by("completed", "created")
    return {"items": items}


@auth.require_authenticated
@auth.require_superuser
def post(request):
    """Create a todo item."""
    data = json.loads(request.body)
    if "content" in data:
        content = data["content"]
    else:
        return HttpResponseBadRequest("Content is required to create a todo item")
    content = content.strip()
    if not content:
        return HttpResponseBadRequest("Todo item content cannot be empty")
    return TodoItem.objects.create(content=content)
