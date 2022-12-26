from functools import update_wrapper
from typing import Callable, Optional

from .views.handler import Handler, Impl


def handler(
    method: str,
    *,
    path="",
    loader=False,
    cache_time=0,
    private=False,
    cache_control: Optional[dict] = None,
    vary_on=("Accept", "Accept-Encoding", "Accept-Language"),
) -> Callable[[Impl], Handler]:
    """Wrap a function to produce a `Handler`.

    If a `path` isn't specified, the handler's path will be derived from
    its function name (replacing underscores with dashes).

    If `path` is equal to `method`, `path` will be set to `""`.

    Use this decorator to:

    1. Add a handler at a subpath.
       a. Specify that a subpath handler should be used as the loader
          for a route rather than using the default `get` handler.
    2. Configure a handler with caching.
    3. Configure a handler's Vary headers.

    Args:
        method: Lower case HTTP method
        path: Handler subpath
        loader: Should this handler be used as the route's loader?
        cache_time: Cache time in seconds
        private: Whether `Cache-Control` should be set as private
        cache_control: Any valid cache control directive
        vary_on: Names of headers to vary on (sets the `Vary` header)

    """

    def wrapper(impl: Impl) -> Handler:
        nonlocal path

        if not path and path != method:
            path = impl.__name__.replace("_", "-")

        return update_wrapper(
            Handler(
                impl,
                method,
                path=path,
                is_loader=loader,
                cache_time=cache_time,
                private=private,
                cache_control=cache_control,
                vary_on=vary_on,
            ),
            impl,
        )

    return wrapper
