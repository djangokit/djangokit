import json
import logging
from dataclasses import dataclass, field, fields
from hashlib import sha1
from inspect import signature
from pathlib import Path
from typing import Callable, Optional, Sequence

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.middleware import csrf
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.views.decorators.cache import cache_page

from ..build import run_bundle
from ..http import JsonResponse
from ..serializers import JsonEncoder

log = logging.getLogger(__name__)

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
    vary_on: Sequence[str] = ("Accept", "Accept-Encoding", "Accept-Language")

    # Derived
    has_cache_config: bool = field(init=False)
    pass_handler_to_impl: bool = field(init=False)

    def __init__(self, impl: Impl, method: str, path: str, **kwargs):
        method = method.lower()

        self.impl = impl
        self.method = method
        self.path = path
        self.has_cache_config = False

        field_names = set(f.name for f in fields(self))
        for name, val in kwargs.items():
            if name not in field_names:
                raise TypeError(
                    f"__init__() got an unexpected keyword argument {name!r}"
                )
            setattr(self, name, val)
            if name in ("cache_time", "private", "cache_control", "vary_on"):
                self.has_cache_config = True

        self.__post_init__()

    def __post_init__(self):
        if self.is_loader and self.method != "get":
            raise ImproperlyConfigured(f"Cannot use {self.method} handler as a loader.")

        if self.cache_time:
            if self.method in ("get", "head"):
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

        spec = signature(self.impl)
        if "djangokit_handler" in spec.parameters:
            self.pass_handler_to_impl = True
        elif any(p.kind is p.VAR_KEYWORD for p in spec.parameters.values()):
            self.pass_handler_to_impl = True
        else:
            self.pass_handler_to_impl = False

    def set_cache_config(self, config):
        for n, v in config.items():
            setattr(self, n, v)
        self.has_cache_config = True
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
        if self.pass_handler_to_impl:
            kwargs["djangokit_handler"] = self
        result = self.impl(request, *args, **kwargs)
        response = self.get_response(request, result)
        self.apply_cache_config(request, response)
        return response

    def __call__(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.call(request, *args, **kwargs)

    def get_response(self, request: HttpRequest, result) -> HttpResponse:
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

    def apply_cache_config(self, request: HttpRequest, response: HttpResponse):
        if self.private or request.user.is_authenticated:
            patch_cache_control(response, private=True)
        elif self.cache_time:
            patch_cache_control(response, public=True)

        if self.cache_control:
            patch_cache_control(response, **self.cache_control)

        if self.vary_on and not self.private:
            patch_vary_headers(response, self.vary_on)


def render(request, *args, **kwargs):
    """Render app template.

    If SSR is enabled in the app's settings, this will also do SSR
    and inject the markup into the app template.

    """
    handler = kwargs["djangokit_handler"]
    dk_settings = settings.DJANGOKIT
    user = request.user
    context = {"settings": dk_settings}

    # XXX: We don't do SSR for logged-in users for now, regardless
    #      of SSR setting. This is mainly to avoid issues with React
    #      SSR hydration.
    do_ssr = dk_settings.ssr and not user.is_authenticated

    if do_ssr:
        bundle_path = handler.ssr_bundle_path

        # XXX: Calling get_token() will force the CSRF cookie to
        #      *always* be set, which conflicts with caching. Need
        #      to figure out a way to lazily access the token only
        #      when needed.
        masked_csrf_token = csrf.get_token(request)

        csrf_token = csrf._unmask_cipher_token(masked_csrf_token)
        current_user_data = dk_settings.current_user_serializer(user)
        current_user_json = json.dumps(current_user_data, cls=JsonEncoder)
        loader = handler.loader
        if loader is not None:
            loader_kwargs = kwargs.copy()
            if not loader.pass_handler_to_impl:
                loader_kwargs.pop("djangokit_handler")
            data = loader.impl(request, *args, **loader_kwargs)
            data = json.dumps(data, cls=JsonEncoder)
        else:
            data = ""
        argv = [request.path, csrf_token, current_user_json, data]

        key = ":".join((str(bundle_path), *argv))
        key = sha1(key.encode("utf-8")).hexdigest()
        markup = cache.get(key)

        if markup is None:
            log.debug("Generating and caching SSR markup with args: %s", argv)
            markup = run_bundle(bundle_path, argv)
            cache.set(key, markup, None)

        context["markup"] = markup
    else:
        # XXX: This is a hack to force the CSRF cookie to *always*
        #      be set in order to avoid 403 errors. This conflicts
        #      with caching. Need to figure out a way to lazily
        #      access the token only when needed.
        csrf.get_token(request)
        context["markup"] = "Loading..."

    return TemplateResponse(request, handler.template_name, context)


@dataclass
class PageHandler(Handler):
    """Handler for rendering pages."""

    impl: Impl = render
    method: str = "get"
    path: str = ""

    template_name: str = "djangokit/app.html"
    """Template used to render page for both CSR & SSR."""

    ssr_bundle_path: Path = Path()
    """Path to bundle used to render SSR markup."""

    loader: Optional[Handler] = None
    """The handler that is the loader for this view."""
