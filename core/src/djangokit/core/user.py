from typing import Any, Dict


def serialize_current_user(user: Any) -> Dict[str, Any]:
    """Serialize the current user into a dict.

    Serialization of the current user can be customized by adding
    `serialize_current_user` to your `DJANGOKIT` settings::

        # settings.py
        DJANGOKIT = {
            "serialize_current_user": "my_package.user.serialize_current_user",
            ...
        }

    `serialize_current_user` must point at a function that takes a user
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
