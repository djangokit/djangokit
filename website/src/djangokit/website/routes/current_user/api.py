def get(request):
    user = request.user
    if not user.is_authenticated:
        return {
            "username": None,
            "email": None,
            "isAnonymous": True,
            "isAuthenticated": False,
            "isStaff": False,
            "isSuperuser": False,
        }
    return {
        "username": user.username,
        "email": user.email,
        "isAnonymous": user.is_anonymous,
        "isAuthenticated": user.is_authenticated,
        "isStaff": user.is_staff,
        "isSuperuser": user.is_superuser,
    }
