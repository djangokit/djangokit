from django.http import JsonResponse


def get_current_user(request):
    user = request.user
    if user.is_authenticated:
        data = {
            "username": user.username,
            "email": user.email,
            "isAnonymous": user.is_anonymous,
            "isAuthenticated": user.is_authenticated,
            "isStaff": user.is_staff,
            "isSuperuser": user.is_superuser,
        }
    else:
        data = {
            "username": None,
            "email": None,
            "isAnonymous": True,
            "isAuthenticated": False,
            "isStaff": False,
            "isSuperuser": False,
        }
    return JsonResponse(data)
