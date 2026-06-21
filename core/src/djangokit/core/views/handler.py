import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Callable, Optional, Sequence, Union

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.views.decorators.cache import cache_page

from ..http import JsonResponse
from ..problem import Problem

log = logging.getLogger(__name__)

Impl = Callable
"""A handler's implementation method."""


Result = Union[
    None,
    dict,
    models.Model,
    str,
    Problem,
    HttpResponse,
    int,
    tuple[int, dict],
    tuple[int, models.Model],
    tuple[int, str],
]
"""The result of calling a handler implementation."""

REDIRECT_STATUS_CODES = (
    HTTPStatus.MOVED_PERMANENTLY,  # 301
    HTTPStatus.FOUND,  # 302
    HTTPStatus.SEE_OTHER,  # 303
    HTTPStatus.TEMPORARY_REDIRECT,  # 307
    HTTPStatus.PERMANENT_REDIRECT,  # 308
)

PERMANENT_REDIRECT_STATUS_CODES = (
    HTTPStatus.MOVED_PERMANENTLY,  # 301
    HTTPStatus.PERMANENT_REDIRECT,  # 308
)

PRESERVE_REQUEST_REDIRECT_STATUS_CODES = (
    HTTPStatus.TEMPORARY_REDIRECT,  # 307
    HTTPStatus.PERMANENT_REDIRECT,  # 308
)


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

    Handler functions can return one of the following types:

    1. None, which will be converted to a 204 No Content response.
    2. A dict, which will be converted to a JSON response with a 200
       status code.
    3. A Django model instance, which will be converted to a JSON
       response with a 200 status code.
    4. A string, which will be converted to a 200 response with the
       specified body content.
    5. A :class:`Problem` instance.
    6. A Django response object when total control is needed over the
       response.
    7. An HTTP status code, which will be converted to an empty response
       with the specified status code. If the status code is a redirect
       status code, a redirect to the current page will be returned.
    8. An HTTP status code *and* a dict, which will be converted to a
       JSON response with the specified status code.
    9. An HTTP status code *and* a Django model instance, which will be
       converted to a JSON response with the specified status code.
    10. An HTTP status code *and* a string, which will be converted to a
        response with the specified status code and body. If the status
        code is a redirect status code, a redirect to the specified path
        will be returned.

    If there's no handler corresponding to the request's method, a 405
    response will be returned.

    Raises:
        TypeError:
            When the return value from a handler isn't valid, we
            raise a `TypeError` because that's a programming error.

    """

    impl: Impl
    method: str
    path: str
    is_loader: bool = False
    cache_time: Optional[int] = None
    private: Optional[bool] = None
    vary_on: Optional[Sequence[str]] = None
    cache_control: Optional[dict] = None

    def __post_init__(self):
        self.check()

    def check(self):
        if self.is_loader and self.method != "get":
            raise ImproperlyConfigured(f"Cannot use {self.method} handler as a loader.")

        if self.cache_time is not None:
            if self.method in ("get", "head", "*"):
                # XXX: Not sure why, but wrapping __call__ directly
                #      doesn't work right.
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

    def set_defaults(self, **defaults):
        """Set defaults for attributes that aren't set."""
        for n, v in defaults.items():
            if v is not None and getattr(self, n) is None:
                setattr(self, n, v)
        self.__post_init__()

    def call(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Call the handler implementation & handle caching.

        For authenticated users, responses are marked as private and
        are *not* cached.

        For unauthenticated users, responses are cached based on the
        specified `vary_on` headers.

        .. note::
            Django will automatically add `Cookie` to the `Vary` header
            when the CSRF cookie is set (and in other cases, such as
            when the session is accessed). Given the way page rendering
            currently works, where the CSRF cookie is *always* set,
            caching of pages will be per-user.

        .. todo::
            Look into fixing the above issue with page rendering. This
            might required detecting if a page uses the CSRF token or
            something along those lines.

        """
        result = self.impl(request, *args, **kwargs)
        response = self.get_response(request, result)
        if request.method in ("GET", "HEAD"):
            self.apply_cache_config(request, response)
        return response

    def __call__(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.call(request, *args, **kwargs)

    def get_response(self, request: HttpRequest, result: Result) -> HttpResponse:
        if isinstance(result, HttpResponse):
            return result

        status, data = self.get_status_and_data_for_result(request, result)

        if status in REDIRECT_STATUS_CODES:
            to = data
            if not isinstance(to, str):
                raise TypeError(
                    f"Redirect location must be a string; got {type(to)}: {to!r}."
                )
            permanent = status in PERMANENT_REDIRECT_STATUS_CODES
            preserve_request = status in PRESERVE_REQUEST_REDIRECT_STATUS_CODES
            response = redirect(
                to,
                permanent=permanent,
                preserve_request=preserve_request,
            )
            # Django doesn't handle 303, so ensure the correct status is
            # set.
            response.status_code = status
            return response

        match data:
            case None:
                return HttpResponse(status=204)
            case dict():
                return JsonResponse(data, status=status)
            case models.Model():
                return JsonResponse(data, status=status)
            case str():
                return HttpResponse(data, status=status)
            case Problem():
                return JsonResponse(data, status=status)

        raise TypeError(
            f"Handler returned unexpected data of type {type(data)}: {data!r}."
        )

    def get_status_and_data_for_result(
        self,
        request: HttpRequest,
        result: Result,
    ) -> tuple[int, Any]:
        """Get the status and data for a handler result."""
        match result:
            case None:
                return 204, None
            case int() if result in REDIRECT_STATUS_CODES:
                return result, request.path
            case int():
                prefers_json = getattr(request, "prefers_json", False)
                data = {} if prefers_json else ""
                return result, data
            case dict():
                return 200, result
            case models.Model():
                return 200, result
            case str():
                return 200, result
            case Problem():
                return result.status, result

        # At this point, the result must be a tuple containing an HTTP
        # status code and a dict, model instance, or string. Anything
        # else will cause a type error.

        if isinstance(result, tuple):
            if len(result) != 2:
                raise TypeError(
                    f"Handler returned tuple with {len(result)} item(s): {result!r}. "
                    "(expected 2)."
                )

            status, data = result

            if not isinstance(status, int):
                raise TypeError(
                    f"Handler returned unexpected HTTP status code type {type(status)} "
                    f"{status!r} (expected int)."
                )

            return status, data

        raise TypeError(
            f"Handler returned unexpected object of type {type(result)}: {result!r}."
        )

    def apply_cache_config(self, request: HttpRequest, response: HttpResponse):
        if request.method not in ("GET", "HEAD"):
            return

        if self.cache_control:
            patch_cache_control(response, **self.cache_control)

        if self.private or request.user.is_authenticated:
            patch_cache_control(response, private=True)
        elif self.cache_time is not None:
            patch_cache_control(response, public=True)
            if self.vary_on:
                patch_vary_headers(response, self.vary_on)
