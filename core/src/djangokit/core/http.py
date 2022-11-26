from django.db import models
from django.http import JsonResponse as DjangoJsonResponse

from .serializers import JsonEncoder


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, encoder=JsonEncoder, safe=True, **kwargs):
        if safe and isinstance(data, models.Model):
            safe = False
        super().__init__(data, encoder=encoder, safe=safe, **kwargs)
