from os import getenv


def get(_request):
    return {
        "env": getenv("ENV", "development"),
        "version": getenv("VERSION"),
    }
