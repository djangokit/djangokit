from django.http import JsonResponse

from ..conf import settings


def get_current_user(request):
    data = settings.current_user_serializer(request.user)
    return JsonResponse(data)
