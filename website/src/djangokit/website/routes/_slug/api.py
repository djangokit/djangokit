from typing import Optional

from django.shortcuts import get_object_or_404
from pydantic import BaseModel, ValidationError, root_validator

from ... import auth
from ...models import Page


def get(_request, slug):
    return get_object_or_404(Page, slug=slug)


class PatchSchema(BaseModel):
    published: Optional[bool] = None
    order: Optional[int] = None

    @root_validator
    def ensure_at_least_one_value(cls, values):
        if any(name in values for name in cls.__fields__):
            return values
        raise ValueError("PATCH of Page requires at least one field")


@auth.require_authenticated
@auth.require_superuser
def patch(request, slug):
    item = get_object_or_404(Page, slug=slug)

    try:
        data = PatchSchema(**request.data)
    except ValidationError as exc:
        messages = [err["msg"] for err in exc.errors()]
        return 400, {"messages": messages}

    for name in data.__fields__:
        val = getattr(data, name)
        if val is not None:
            setattr(item, name, val)

    item.save()
    item.refresh_from_db()
    return item
