from django.db import models
from django.http import HttpRequest
from django.http import JsonResponse as DjangoJsonResponse

from .serializers import JsonEncoder


def make_request(path="/", path_info=None):
    """Make a request object with the specified path."""
    request = HttpRequest()
    request.path = path
    request.path_info = path_info or path
    return request


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, encoder=JsonEncoder, safe=True, **kwargs):
        if safe and isinstance(data, models.Model):
            safe = False
        super().__init__(data, encoder=encoder, safe=safe, **kwargs)
