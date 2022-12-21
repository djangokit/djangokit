from django.db import models
from django.http import HttpRequest
from django.http import JsonResponse as DjangoJsonResponse

from .serializers import JsonEncoder


def make_request(**attrs):
    """Make a request object with the specified attributes."""
    attrs.setdefault("method", "GET")

    path = attrs.setdefault("path", "/")
    path_info = attrs.setdefault("path_info", path)

    meta = attrs.setdefault("META", {})
    meta.setdefault("PATH_INFO", path_info)

    request = HttpRequest()

    for name, val in attrs.items():
        setattr(request, name, val)

    return request


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, encoder=JsonEncoder, safe=True, **kwargs):
        if safe and isinstance(data, models.Model):
            safe = False
        super().__init__(data, encoder=encoder, safe=safe, **kwargs)
