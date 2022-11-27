from django.http import JsonResponse
from django.middleware import csrf


def get_token(request):
    return JsonResponse({"csrfToken": csrf.get_token(request)})
