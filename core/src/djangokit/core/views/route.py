import json
import logging
import os
from collections import defaultdict
from functools import lru_cache
from hashlib import sha1
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional, Tuple, Union

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse, Http404
from django.middleware import csrf
from django.utils.cache import patch_cache_control
from django.utils.decorators import classonlymethod
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic.base import TemplateResponseMixin

from ..build import run_bundle
from ..serializers import JsonEncoder
from .handler import Handler

log = logging.getLogger(__name__)


class RouteView(TemplateResponseMixin, View):

    path: Path
    """Absolute path to route directory."""

    template_name = "djangokit/app.html"
    """Template used to render page for both CSR & SSR."""

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

    handlers: Dict[str, List[Handler]] = {}
    """Handlers for view (map of HTTP method name to handlers).
    
    These are discovered from the route's handler module. Any function
    in the handler module that is named after a known HTTP method name
    is considered a handler as is any function that is explicitly
    declared as a handler using the `handler` decorator.

    """

    loader: Optional[Handler] = None
    """The handler that is the loader for this view."""

    ssr_bundle_path: Path = Path()
    """Path to bundle used to render SSR markup."""

    @classonlymethod
    def as_view_from_node(
        cls,
        node,
        *,
        template_name: Optional[str] = None,
        ssr_bundle_path: Optional[Union[str, Path]] = None,
        cache_time=0,
    ) -> Tuple[Callable,]:
        page_module = node.page_module
        handler_module = node.handler_module

        if handler_module:
            handlers, loader = cls.get_handlers(handler_module)
            if not handlers:
                raise ImproperlyConfigured(
                    f"The handler module {handler_module.__name__} doesn't contain any "
                    "handlers. Expected at least one handler (get, post, etc)."
                )
        else:
            handlers = {}
            loader = None

        ssr_bundle_path = (
            Path(ssr_bundle_path) if ssr_bundle_path else get_ssr_bundle_path()
        )

        view = cls.as_view(
            template_name=template_name or cls.template_name,
            page_module=page_module,
            handler_module=handler_module,
            handlers=handlers,
            loader=loader,
            ssr_bundle_path=ssr_bundle_path,
        )

        if cache_time and (page_module or "get" in handlers or "head" in handlers):
            view = cls.make_cached_view(view, cache_time)

        view.djangokit_handlers = handlers
        return view

    @classonlymethod
    def get_handlers(
        cls,
        module: ModuleType,
    ) -> Tuple[Dict[str, List[Handler]], Optional[Handler]]:
        """Get handlers and loader from `module`.

        Returns:
            - A dict mapping HTTP method names to handlers
            - The handler that's designated as the loader for the route,
              if there is one

        """
        objects = vars(module)
        callables = tuple((n, obj) for n, obj in objects.items() if callable(obj))

        if not callables:
            return {}, None

        module_name = module.__name__
        handlers = defaultdict(dict)
        loader = None

        for name, maybe_handler in callables:
            if isinstance(maybe_handler, Handler):
                handler = maybe_handler
            elif name in cls.http_method_names:
                handler = Handler(maybe_handler, name, path=name)
            else:
                continue

            method = handler.method
            path = handler.path
            method_handlers = handlers[method]

            if path in method_handlers:
                raise ImproperlyConfigured(
                    f"Found duplicate handler path for method {method} in "
                    f"handler module {module_name}: {path}."
                )
            else:
                method_handlers[path] = handler

            if handler.is_loader:
                if handler.method != "get":
                    raise ImproperlyConfigured(
                        "Only a GET handler can be designated as the loader for a "
                        f"route (module = {module_name})."
                    )
                if loader is not None:
                    raise ImproperlyConfigured(
                        "Only one handler per handler module may be "
                        f"designated as the loader (module = {module_name})."
                    )
                loader = handler

            if method == "get" and path == "" and "head" not in handlers:
                handlers["head"][""] = handler

        if loader is None and "get" in handlers and "" in handlers["get"]:
            loader = handlers["get"][""]
            loader.is_loader = True

        return handlers, loader

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
        self.subpath = kwargs.pop("__subpath__")

    def dispatch(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
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
        See class:`Handler` for more information about what handlers can
        return.

        """
        method = request.method.lower()
        subpath = kwargs.pop("__subpath__")
        handlers = self.handlers
        prefers_html = not request.prefers_json

        if (
            method in ("get", "head")
            and subpath == ""
            and (prefers_html or method not in handlers)
            and self.page_module
        ):
            return self.render()

        if method not in handlers:
            if method == "options":
                return self.options(request, *args, **kwargs)
            return self.http_method_not_allowed(request, *args, **kwargs)

        method_handlers = handlers[method]

        if subpath not in method_handlers:
            # XXX: This should never happen?
            log.error(
                f"Subpath not found for method %s in handler module %s: %s",
                method,
                self.handler_module,
                subpath,
            )
            raise Http404

        handler = method_handlers[subpath]
        return handler(request, *args, **kwargs)

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
            current_user_json = json.dumps(current_user_data, cls=JsonEncoder)
            if self.loader is not None:
                data = self.loader.impl(request, *self.args, **self.kwargs)
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
