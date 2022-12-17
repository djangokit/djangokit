from django.conf import settings
from django.http import JsonResponse


def get_current_user(request):
    data = settings.DJANGOKIT.current_user_serializer(request.user)
    return JsonResponse(data)
