from typing import Any, Dict


def current_user_serializer(user: Any) -> Dict[str, Any]:
    """Serialize the current user into a dict.

    Serialization of the current user can be customized by adding
    `current_user_serializer` to your `DJANGOKIT` settings::

        # settings.py
        DJANGOKIT = {
            "current_user_serializer": "my_package.user.current_user_serializer",
            ...
        }

    `current_user_serializer` must point at a function that takes a user
    object and returns an object that can be JSON-serialized (typically
    a dict).

    """
    if user.is_authenticated:
        return {
            "username": user.username,
            "email": user.email,
            "isAnonymous": user.is_anonymous,
            "isAuthenticated": user.is_authenticated,
            "isStaff": user.is_staff,
            "isSuperuser": user.is_superuser,
        }
    return {
        "username": None,
        "email": None,
        "isAnonymous": True,
        "isAuthenticated": False,
        "isStaff": False,
        "isSuperuser": False,
    }
