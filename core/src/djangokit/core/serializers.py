from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import model_to_dict


class JsonEncoder(DjangoJSONEncoder):
    """A JSON encoder that can handle model instances.

    Model instances can define either a `serialize` method or specify
    a `serializer_factory` attribute (usually as a class attribute).

    In the case of a `serialize` method, it will be called with no
    arguments and should return something that can be encoded by the
    standard JSON encoder.

    In the case of a `serializer_factory` attribute (which is typically
    a class, for example a subclass of `marshmallow.schema.Schema`), it
    will be called and should return an object that has a `dump` method.
    The `dump` method will be called with no arguments and should return
    something that can be encoded by the standard JSON encoder.

    If neither `serialize` or `serializer_factory` is present, we fall
    back to Django's `model_to_dict` utility.

    This allows API handlers to return model instances that can be
    automatically serialized to JSON.

    """

    def default(self, o):
        if isinstance(o, models.QuerySet):
            return tuple(self.default(item) for item in o)
        if isinstance(o, models.Model):
            if hasattr(o, "serialize"):
                return o.serialize()
            if hasattr(o, "serializer_factory"):
                serializer = o.serializer_factory()
                return serializer.dump(o)
            return model_to_dict(o)
        return super().default(o)
