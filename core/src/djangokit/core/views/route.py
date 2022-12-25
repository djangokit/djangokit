import json
import logging
import os
from functools import lru_cache
from hashlib import sha1
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, Optional, Union

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.middleware import csrf
from django.shortcuts import redirect
from django.utils.cache import patch_cache_control
from django.utils.decorators import classonlymethod
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic.base import TemplateResponseMixin

from ..build import run_bundle
from ..http import JsonResponse

log = logging.getLogger(__name__)


class RouteView(TemplateResponseMixin, View):

    path: Path
    """Absolute path to route directory."""

    page_module: Optional[str] = None
    """Page module, if present.

    This is a JSX file that exports a default function.

    """

    handler_module: Optional[ModuleType] = None
    """Handler module for this view.

    This module, if present, contains the handlers for this view. Each
    such handler should be a function that takes a `request` as its
    first argument plus any URL pattern keyword arguments (the args for
    handlers are the same as the args for a normal Django view).

    Handlers can return a dict, a model instance, or a response object.
    See :meth:`dispatch` below for more details.

    """

    allowed_methods: Dict[str, Callable] = {}
    """Allowed HTTP methods for view.

    The allowed methods are determined by the presence of a page module
    and/or the handler functions defined in the configured handler
    module.

    """

    ssr_bundle_path: Path = Path()
    template_name = "djangokit/app.html"

    @classonlymethod
    def as_view_from_node(
        cls,
        node,
        cache_time=0,
        ssr_bundle_path: Optional[Union[str, Path]] = None,
    ):
        page_module = node.page_module
        handler_module = node.handler_module
        allowed_methods = {}

        if handler_module:
            for name in dir(handler_module):
                if name in cls.http_method_names:
                    allowed_methods[name] = getattr(handler_module, name)

            if "head" not in allowed_methods and "get" in allowed_methods:
                allowed_methods["head"] = allowed_methods["get"]

            if not allowed_methods:
                raise ImproperlyConfigured(
                    f"The handler module {handler_module.__name__} doesn't contain any "
                    "handlers. Expected at least one handler (get, post, etc)."
                )

        ssr_bundle_path = (
            Path(ssr_bundle_path) if ssr_bundle_path else get_ssr_bundle_path()
        )

        view = cls.as_view(
            page_module=page_module,
            handler_module=handler_module,
            allowed_methods=allowed_methods,
            ssr_bundle_path=ssr_bundle_path,
        )

        if cache_time and (
            page_module or "get" in allowed_methods or "head" in allowed_methods
        ):
            view = cls.make_cached_view(view, cache_time)

        return view

    @classonlymethod
    def make_cached_view(cls, view, cache_time: int):
        """Wrap `view` to add caching.

        For authenticated users, responses are marked as private and
        are *not* cached.

        For unauthenticated users, responses are cached based on the
        `Accept` and `Cookie` headers.

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
        if not cache_time:
            return view

        @cache_page(cache_time)
        @vary_on_headers("Accept")
        def cached_view(request, *args, **kwargs):
            response = view(request, *args, **kwargs)
            public = request.user.is_anonymous
            if public:
                patch_cache_control(response, public=True)
            else:
                patch_cache_control(response, private=True)
            return response

        return cached_view

    def setup(self, request: HttpRequest, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Dispatch request.

        `GET`/`HEAD` handling:

         1. If HTML is preferred and there's a page module, render the
            page.
         2. If HTML is preferred and there's NOT a page module, fall
            through and return the result of the handler (or a 405 if
            there is no handler for the method).
         3. If JSON is preferred but there's no handler for the request
            method and there IS a page module, render the page.
         4. If JSON is preferred but there's no handler for the request
            method and there is NOT a page module, fall through and
            return a 405.

        .. note::
            JSON is preferred whenever the `Accept` header is
            `application/json`. HTML is preferred otherwise.

        All other request methods will always be handled by a handler.

        Handlers can return one of the following:

        1. A dict or a model instance, which will be converted to a JSON
           response with a 200 status code.
        2. A string, which will be converted to a 200 response with the
           specified body content.
        3. An HTTP status code (an `int`), which will be converted to an
           empty response with the specified status code *or* to a
           redirect to / if the status code is 301 or 302.
        4. A status code *and* a dict or model instance, which will be
           converted to a JSON response with the specified status code
           and data.
        5. A status code *and* a string, which will be converted to a
           response with the specified status code and body  *or* to a
           redirect if the status code is 301 or 302.
        6. None, which will be converted to a 204 No Content response.
        7. A Django response object when more control is needed over the
           response.

        If there's no handler corresponding to the request's method, a
        405 response will be returned.

        .. note::
            To redirect, return 301 or 302 and a redirect location.
            E.g., `302, "/login"`. Note that you usually want to use
            302 non-permanent redirects. Note also that trying to
            redirect with data will raise an error (e.g., `302, {}`).

        Raises:
            TypeError:
                When the return value from a handler isn't valid, we
                raise a `TypeError` because that's a programming error.

        """
        method = request.method.lower()
        allowed_methods = self.allowed_methods
        prefers_json = request.prefers_json
        prefers_html = not prefers_json

        if (
            method in ("get", "head")
            and (prefers_html or method not in allowed_methods)
            and self.page_module
        ):
            return self.render()

        if method not in allowed_methods:
            if method == "options":
                return self.options(request, *args, **kwargs)
            return self.http_method_not_allowed(request, *args, **kwargs)

        handler = allowed_methods[method]
        result = handler(request, *args, **kwargs)

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
            elif prefers_json:
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

    def render(self) -> str:
        """Render app template.

        If SSR is enabled in the app's settings, this will also do SSR
        and inject the markup into the app template.

        """
        dk_settings = settings.DJANGOKIT
        request: HttpRequest = self.request
        user = request.user
        context = {"view": self, "settings": dk_settings}

        # XXX: We don't do SSR for logged-in users for now, regardless
        #      of SSR setting. This is mainly to avoid issues with React
        #      SSR hydration.
        do_ssr = dk_settings.ssr and not user.is_authenticated

        if do_ssr:
            bundle_path = self.ssr_bundle_path

            # XXX: Calling get_token() will force the CSRF cookie to
            #      *always* be set, which conflicts with caching. Need
            #      to figure out a way to lazily access the token only
            #      when needed.
            masked_csrf_token = csrf.get_token(request)

            csrf_token = csrf._unmask_cipher_token(masked_csrf_token)
            current_user_data = dk_settings.current_user_serializer(user)
            current_user_json = json.dumps(current_user_data)
            argv = [request.path, csrf_token, current_user_json]

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

        return self.render_to_response(context)


@lru_cache(maxsize=None)
def get_ssr_bundle_path(bundle_name="build/server.bundle.js") -> Path:
    # NOTE: This path never changes for a given deployment/version, so
    #       we only need to look it up once.
    if settings.DEBUG or settings.ENV == "test":
        bundle_path = find(bundle_name)
        if bundle_path:
            return Path(bundle_path)
        raise FileNotFoundError(
            f"Could not find static file for SSR bundle: {bundle_name}"
        )
    else:
        bundle_path = staticfiles_storage.path(bundle_name)
        if os.path.exists(bundle_path):
            return Path(bundle_path)
        raise FileNotFoundError(f"SSR bundle path does not exist: {bundle_path}")
