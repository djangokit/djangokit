"""API for todo item collection."""

from django.http import HttpRequest
from django.shortcuts import redirect

from djangokit.website import auth
from djangokit.website.models import TodoItem


def get(_request):
    """Get all todo items."""
    items = TodoItem.objects.all().order_by("completed", "created")
    return {"items": items}


@auth.require_authenticated
@auth.require_superuser
def post(request: HttpRequest):
    """Create a todo item."""
    data = request.data

    if "content" in data:
        content = data["content"]
    else:
        return 400, "Content is required to create a todo item"

    content = content.strip()

    if not content:
        return 400, "Todo item content cannot be empty"

    if request.is_fetch:
        return TodoItem.objects.create(content=content)

    return redirect("/todos")
