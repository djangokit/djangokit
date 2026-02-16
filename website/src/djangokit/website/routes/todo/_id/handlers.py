from typing import Optional

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from pydantic import BaseModel, ValidationError, model_validator

from .... import auth
from ....models import TodoItem


def get(_request, id):
    return get_object_or_404(TodoItem, id=id)


@auth.require_authenticated
@auth.require_superuser
def delete(_request, id):
    item = get_object_or_404(TodoItem, id=id)
    item.delete()
    return 303, "/todo"


class PatchSchema(BaseModel):
    content: Optional[str] = None
    completed: Optional[bool] = None

    @model_validator(mode="after")
    def ensure_at_least_one_value(self):
        if self.content is not None or self.completed is not None:
            return self
        raise ValueError("PATCH TodoItem requires at least one field")


@auth.require_authenticated
@auth.require_superuser
def patch(request: HttpRequest, id):
    item = get_object_or_404(TodoItem, id=id)

    try:
        data = PatchSchema(**request.data)
    except ValidationError as exc:
        for err in exc.errors():
            messages.error(request, err["msg"])
        return 303, "/todo"

    for name in PatchSchema.model_fields:
        if name == "completed":
            continue
        val = getattr(data, name)
        if val is not None:
            setattr(item, name, val)

    completed = data.completed
    if completed is not None:
        item.completed = timezone.now() if completed else None

    item.save()
    return 303, "/todo"
