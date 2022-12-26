import logging
import os
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import classonlymethod
from django.views import View

from .handler import Handler, PageHandler

log = logging.getLogger(__name__)


class RouteView(View):

    page_module: Optional[str] = None
    """Page module, if present.

    This is a JSX file that exports a default function.

    """

    page_handler: Optional[PageHandler] = None
    """Handler used to render page."""

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

    @classonlymethod
    def as_view_from_node(
        cls,
        node,
        *,
        cache_time=0,
        private: bool = False,
        cache_control: Optional[dict] = None,
        vary_on: Sequence[str] = ("Accept", "Accept-Encoding", "Accept-Language"),
        template_name: Optional[str] = "djangokit/app.html",
        ssr_bundle_path: Optional[Union[str, Path]] = None,
        loader: Optional[Handler] = None,
    ) -> Tuple[Callable[[HttpRequest], HttpResponse]]:
        page_module = node.page_module
        handler_module = node.handler_module

        if handler_module:
            handlers, discovered_loader = cls.get_handlers(
                handler_module,
                cache_time,
                private,
                cache_control,
                vary_on,
            )
            if not handlers:
                raise ImproperlyConfigured(
                    f"The handler module {handler_module.__name__} doesn't contain any "
                    "handlers. Expected at least one handler (get, post, etc)."
                )
            if loader is None:
                loader = discovered_loader
        else:
            handlers = {}

        if page_module:
            ssr_bundle_path = (
                Path(ssr_bundle_path) if ssr_bundle_path else get_ssr_bundle_path()
            )
            page_handler = PageHandler(
                template_name=template_name,
                ssr_bundle_path=ssr_bundle_path,
                loader=loader,
                cache_time=cache_time,
                private=private,
                cache_control=cache_control,
                vary_on=vary_on,
            )
        else:
            page_handler = None

        return cls.as_view(
            page_module=page_module,
            page_handler=page_handler,
            handler_module=handler_module,
            handlers=handlers,
        )

    @classonlymethod
    def get_handlers(
        cls,
        module: ModuleType,
        cache_time: int,
        private: bool,
        cache_control: Optional[dict],
        vary_on: Sequence[str],
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

        cache_config = {
            "cache_time": cache_time,
            "private": private,
            "cache_control": cache_control,
            "vary_on": vary_on,
        }

        for name, maybe_handler in callables:
            if isinstance(maybe_handler, Handler):
                handler = maybe_handler
                if not handler.has_cache_config:
                    handler.set_cache_config(cache_config)
            elif name in cls.http_method_names:
                method = name
                handler_cache_args = cache_config.copy() if method == "get" else {}
                handler = Handler(maybe_handler, method, "", **handler_cache_args)
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
        page_handler = self.page_handler
        handlers = self.handlers
        subpath = kwargs.pop("__subpath__")
        prefers_html = not request.prefers_json

        if (
            method in ("get", "head")
            and subpath == ""
            and (prefers_html or method not in handlers)
            and page_handler
        ):
            return page_handler(request, *args, **kwargs)

        if method not in handlers:
            if method == "options":
                return self.options(request, *args, **kwargs)
            return self.http_method_not_allowed(request, *args, **kwargs)

        method_handlers = handlers[method]
        handler = method_handlers[subpath]
        return handler(request, *args, **kwargs)


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
        hashed_bundle_name = staticfiles_storage.stored_name(bundle_name)
        bundle_path = staticfiles_storage.path(hashed_bundle_name)
        if os.path.exists(bundle_path):
            return Path(bundle_path)
        raise FileNotFoundError(f"SSR bundle path does not exist: {bundle_path}")
