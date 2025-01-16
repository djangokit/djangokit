from typing import Optional

from django.shortcuts import get_object_or_404
from pydantic import BaseModel, ValidationError, model_validator

from ... import auth
from ...models import Page


def get(_request, slug):
    return get_object_or_404(Page, slug=slug)


class PatchSchema(BaseModel):
    published: Optional[bool] = None
    before: Optional[int] = None

    @model_validator(mode="after")
    def ensure_at_least_one_value(self, values):
        if any(name in values for name in self.model_fields):
            return values
        raise ValueError("PATCH of Page requires at least one field")


@auth.require_authenticated
@auth.require_superuser
def patch(request, slug):
    page = get_object_or_404(Page, slug=slug)

    try:
        data = PatchSchema(**request.data)
    except ValidationError as exc:
        messages = [err["msg"] for err in exc.errors()]
        return 400, {"messages": messages}

    for name in data.__fields__:
        if name == "before":
            continue
        val = getattr(data, name)
        if val is not None:
            setattr(page, name, val)

    if data.before is not None:
        all_pages = list(Page.objects.all())
        for p in all_pages:
            if p.id == data.before:
                before_page = p
                all_pages.remove(page)
                before_index = all_pages.index(before_page)
                all_pages.insert(before_index, page)
                for order, q in enumerate(all_pages):
                    q.order = order
                    q.save()
                break
        else:
            return 404, f"Before page with ID not found: {data.before}"

    page.save()
    page.refresh_from_db()
    return page
