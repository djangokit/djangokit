from django.http import JsonResponse

from ..conf import settings


def get_current_user(request):
    data = settings.serialize_current_user(request.user)
    return JsonResponse(data)
