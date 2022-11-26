"""API for todo item collection."""
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest

from ...models import TodoItem


def get(_request):
    """Get all todo items."""
    items = TodoItem.objects.all().order_by("completed", "created")
    items = [item.as_dict() for item in items]
    return {"items": items}


@login_required
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
    item = TodoItem.objects.create(content=content)
    return item.as_dict()
