from ...decorators import handler


def get(_request):
    return {"slug": "home"}


@handler("get", cache_time=5)
def stuff(_request, __ext__=None):
    return {"slug": "stuff", "ext": __ext__}


@handler("get", cache_time=10, vary_on=["Accept", "Accept-Language"])
def things(_request):
    return {"slug": "things"}


@handler("get", private=True)
def private(_request):
    return {"slug": "private"}
