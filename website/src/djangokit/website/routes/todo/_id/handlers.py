from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils import timezone
from pydantic import BaseModel, ValidationError, root_validator

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
        if any(name in values for name in cls.__fields__):
            return values
        raise ValueError("PATCH of Page requires at least one field")


@auth.require_authenticated
@auth.require_superuser
def patch(request, id):
    item = get_object_or_404(TodoItem, id=id)

    try:
        data = PatchSchema(**request.data)
    except ValidationError as exc:
        messages = [err["msg"] for err in exc.errors()]
        return 400, {"messages": messages}

    for name in data.__fields__:
        if name == "completed":
            continue
        val = getattr(data, name)
        if val is not None:
            setattr(item, name, val)

    completed = data.completed
    if completed is not None:
        item.completed = timezone.now() if completed else None

    item.save()
    item.refresh_from_db()
    return item
