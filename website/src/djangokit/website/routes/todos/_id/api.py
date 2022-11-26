"""API for individual todo items."""
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from marshmallow import Schema, ValidationError, fields, validates_schema

from djangokit.website import auth
from djangokit.website.models import TodoItem


def get(_request, id):
    return get_object_or_404(TodoItem, id=id)


@auth.require_authenticated
@auth.require_superuser
def delete(_request, id):
    item = get_object_or_404(TodoItem, id=id)
    item.delete()


class PatchSchema(Schema):
    content = fields.String(required=False)
    completed = fields.Boolean(required=False)

    @validates_schema()
    def validate_schema(self, data, **kwargs):
        if not data:
            raise ValidationError("PATCH of TodoItem requires at least one field")


@auth.require_authenticated
@auth.require_superuser
def patch(request, id):
    item = get_object_or_404(TodoItem, id=id)

    try:
        data = PatchSchema().loads(request.body)
    except ValidationError as err:
        return 400, {"messages": err.messages}

    if "content" in data:
        item.content = data["content"]

    if "completed" in data:
        completed = data["completed"]
        item.completed = now() if completed else None

    item.save()
