import json
from functools import partial

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms import model_to_dict


class JsonEncoder(DjangoJSONEncoder):
    """A JSON encoder that can handle model instances.

    Model instances can define a `serialize` method that will be called
    with no arguments and should return something that can be encoded by
    the standard JSON encoder.

    If the model doesn't have a `serialize` method, we fall back to
    Django's `model_to_dict` utility.

    This allows route handlers to return model instances that can be
    automatically serialized to JSON.

    """

    def default(self, o):
        if isinstance(o, models.QuerySet):
            return tuple(o)
        if isinstance(o, models.Model):
            if hasattr(o, "serialize"):
                try:
                    return o.serialize()
                except Exception as exc:
                    # NOTE: The default method can apparently only raise
                    #       ValueErrors. Any other exception type will
                    #       cause the dev server to shut down with no
                    #       indication of what went wrong.
                    model_class = o.__class__
                    class_name = f"{model_class.__module__}.{model_class.__name__}"
                    exc_class = exc.__class__
                    exc_class_name = f"{exc_class.__module__}.{exc_class.__qualname__}"
                    exc_str = " ".join(str(exc).split())
                    raise ValueError(
                        "Model serialization failed when calling "
                        f"{class_name}.serialize(). Original exception: "
                        f"{exc_class_name}: {exc_str}"
                    ) from None
            return model_to_dict(o)
        return super().default(o)


dump_json = partial(json.dumps, cls=JsonEncoder)
