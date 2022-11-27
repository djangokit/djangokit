from django.middleware.csrf import get_token


def get(request):
    return {"csrfToken": get_token(request)}
