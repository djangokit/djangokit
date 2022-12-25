from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.views.decorators.cache import cache_page

from ..http import JsonResponse

Impl = Callable


@dataclass
class Handler:
    """Wrapper for route handlers.

    This is used to store the configuration for a handler function.

    .. note::
        Instead of using this directly, you generally want to use the
        `@handler` decorator.

    Args:
        impl: The function that implements the handler
        method: Lower case HTTP method
        path: Handler subpath
        is_loader: Should this handler be used as the route's loader?
        cache_time: Cache time in seconds
        private: Whether `Cache-Control` should be set as private
        cache_control: Any valid cache control directive
        vary_on: Names of headers to vary on (sets the `Vary` header)

    Handler functions can return one of the following:

    1. A dict or a model instance, which will be converted to a JSON
       response with a 200 status code.
    2. A string, which will be converted to a 200 response with the
       specified body content.
    3. An HTTP status code (an `int`), which will be converted to an
       empty response with the specified status code, unless the status
       code is 301 or 302, in which case a redirect to the site root
       will be returned.
    4. A status code *and* a dict or model instance, which will be
       converted to a JSON response with the specified status code and
       data.
    5. A status code *and* a string, which will be converted to a
       response with the specified status code and body  *or* to a
       redirect if the status code is 301 or 302.
    6. None, which will be converted to a 204 No Content response.
    7. A Django response object when more control is needed over the
       response.

    If there's no handler corresponding to the request's method, a 405
    response will be returned.

    .. note::
        To redirect, return 301 or 302 and a redirect location. E.g.,
        `302, "/login"`. Note that you usually want to use 302
        non-permanent redirects. Note also that trying to redirect with
        data will raise an error (e.g., `302, {}`).

    Raises:
        TypeError:
            When the return value from a handler isn't valid, we
            raise a `TypeError` because that's a programming error.

    """

    impl: Impl
    method: str
    path: str
    is_loader: bool = False
    cache_time: int = 0
    private: bool = False
    cache_control: Optional[dict] = None
    vary_on: Sequence[str] = ("Accept",)

    def __post_init__(self):
        self.method = self.method.lower()

        if not self.path:
            self.path = self.impl.__name__.replace("_", "-")
        if self.path == self.method:
            self.path = ""

        if self.is_loader and self.method != "get":
            raise ImproperlyConfigured(f"Cannot use {self.method} handler as a loader.")

        if self.cache_time:
            if self.method in ("get", "head"):
                self.call = cache_page(self.cache_time)(self.call)
            else:
                raise ImproperlyConfigured(
                    f"Cannot specify cache time for {self.method} handler."
                )
            if self.private:
                # XXX: Is this right? The reason for doing this is that
                #      Django will skip caching if cache control is set
                #      to private, and raising an error here will avoid
                #      unexpected results.
                raise ImproperlyConfigured("Cannot use private with cache_time.")

    def __call__(self, request, *args, **kwargs):
        return self.call(request, *args, **kwargs)

    def call(self, request, *args, **kwargs):
        result = self.impl(request, *args, **kwargs)
        response = self.get_response(request, result)

        if self.private:
            patch_cache_control(response, private=True)
        elif self.cache_time:
            patch_cache_control(response, public=True)

        if self.cache_control:
            patch_cache_control(response, **self.cache_control)

        if self.vary_on:
            patch_vary_headers(response, self.vary_on)

        return response

    def get_response(self, request, result) -> HttpResponse:
        if result is None:
            return HttpResponse(204)

        # XXX: Most common case?
        if isinstance(result, (dict, models.Model)):
            return JsonResponse(result)

        if isinstance(result, str):
            return HttpResponse(result)

        if isinstance(result, int):
            status = result
            if status in (301, 302):
                data = "/"
            elif request.prefers_json:
                data = {}
            else:
                data = ""
            result = (status, data)

        if isinstance(result, tuple):
            if len(result) != 2:
                raise TypeError(
                    f"Handler returned tuple with {len(result)} item(s): {result!r}. "
                    "(expected 2)."
                )

            status, data = result

            if not isinstance(status, int):
                raise TypeError(
                    f"Handler returned unexpected HTTP status type {type(status)} "
                    "(expected int)"
                )

            if status in (301, 302):
                to = data
                if not isinstance(to, str):
                    raise TypeError(
                        f"Redirect location should be a string; got "
                        f"{to}: {type(to)}."
                    )
                permanent = status == 301
                return redirect(to, permanent=permanent)

            if isinstance(data, (dict, models.Model)):
                return JsonResponse(data, status=status)

            if isinstance(data, str):
                return HttpResponse(data, status=status)

            raise TypeError(
                f"Handler returned unexpected data type {type(data)} "
                "(expected dict, Model, or str)"
            )

        # XXX: Least common case?
        if isinstance(result, HttpResponse):
            return result

        raise TypeError(
            f"Handler returned unexpected object of type {type(result)}: {result!r}. "
            "Expected dict, Model, int, Tuple[int, dict], Tuple[int, Model], None or "
            "HttpResponse)."
        )
