"""API for individual todo items."""
from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from pydantic import BaseModel, root_validator, ValidationError

from .... import auth
from ....models import TodoItem


def get(_request, id):
    return get_object_or_404(TodoItem, id=id)


@auth.require_authenticated
@auth.require_superuser
def delete(_request, id):
    item = get_object_or_404(TodoItem, id=id)
    item.delete()


class PatchSchema(BaseModel):
    content: Optional[str] = None
    completed: Optional[bool] = None

    @root_validator
    def ensure_at_least_one_value(cls, values):
        content = values.get("content")
        completed = values.get("completed")
        if content is None and completed is None:
            raise ValueError("PATCH of TodoItem requires at least one field")
        return values


@auth.require_authenticated
@auth.require_superuser
def patch(request, id):
    item = get_object_or_404(TodoItem, id=id)

    try:
        data = PatchSchema(**request.data)
    except ValidationError as exc:
        messages = [err["msg"] for err in exc.errors()]
        return 400, {"messages": messages}

    if data.content is not None:
        item.content = data.content

    if data.completed is not None:
        item.completed = now() if data.completed else None

    item.save()
    item.refresh_from_db()
    return item
