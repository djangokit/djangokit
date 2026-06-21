import json
from functools import partial
from typing import Any, Protocol, runtime_checkable

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import model_to_dict


@runtime_checkable
class JsonSerializable(Protocol):
    """Protocol for types that can be serialized as JSON."""

    def to_json_value(self) -> Any:
        """Convert object to a value that can be serialized as JSON."""
        ...


class JsonEncoder(DjangoJSONEncoder):
    """JSON encoder that handles additional types.

    In addition to the types handled by the standard library and Django
    JSON encoders, this encoder adds support for the following:

    - Any type that implements the :class:`JsonSerializable` protocol.
    - Model instances that don't implement the :class:`JsonSerializable`
      protocol will be serialized with Django's `model_to_dict` utility.
    - Django queryset. A queryset will be materialized as a tuple.

    """

    def default(self, o):
        match o:
            case JsonSerializable():
                return o.to_json_value()
            case models.Model():
                return model_to_dict(o)
            case models.QuerySet():
                return tuple(o)
        return super().default(o)


dump_json = partial(json.dumps, cls=JsonEncoder)
