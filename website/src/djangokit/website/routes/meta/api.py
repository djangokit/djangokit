from os import getenv

from djangokit.website import auth


def get(request):
    data = {
        "env": getenv("ENV", "development"),
        "version": getenv("VERSION"),
    }

    if auth.is_superuser_request(request):
        data.update(
            {
                # TODO
            }
        )
    return data
