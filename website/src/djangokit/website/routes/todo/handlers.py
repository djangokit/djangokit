from django.http import HttpRequest
from django.shortcuts import redirect

from ... import auth
from ...models import TodoItem


def get(_request):
    """Get all todo items."""
    items = TodoItem.objects.all().order_by("created")
    return {
        "todo": [item for item in items if not item.completed],
        "completed": [item for item in items if item.completed],
    }


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

    item = TodoItem.objects.create(content=content)

    if request.prefers_json:
        return item

    return redirect("/todo")
