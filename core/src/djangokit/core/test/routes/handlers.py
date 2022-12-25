from djangokit.core import handler


def get(_request):
    return {"slug": "home"}


@handler("get", cache_time=5)
def stuff(_request):
    return {"slug": "stuff"}


@handler("get", cache_time=10, vary_on=["Accept"])
def things(_request):
    return {"slug": "things"}


@handler("get", private=True)
def private(_request):
    return {"slug": "private"}
