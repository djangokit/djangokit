import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render as render_template

from ..build import run_bundle
from ..serializers import dump_json
from ..utils import get_unmasked_csrf_token, make_cache_key
from .handler import Handler, Impl

log = logging.getLogger(__name__)


@dataclass
class PageHandler(Handler):
    """Handler for rendering pages."""

    impl: Impl = field(init=False)
    method: str = "get"
    path: str = ""
    is_catchall: bool = False

    template_name: str = "djangokit/app.html"
    """Template used to render page for both CSR & SSR."""

    ssr_bundle_path: Optional[Path] = None
    """Path to bundle used to render SSR markup."""

    loader: Optional[Handler] = None
    """The handler that is the loader for this view."""

    def __post_init__(self):
        self.impl = make_render(self)
        super().__post_init__()


def make_render(handler):
    def render(request, *args, **kwargs):
        """Render app template.

        If SSR is enabled in the app's settings, this will also do SSR
        and inject the markup into the app template.

        """
        dk_settings = settings.DJANGOKIT
        path = request.path
        user = request.user
        context = {"settings": dk_settings}

        csr = dk_settings.csr
        ssr = dk_settings.ssr

        # XXX: We don't do SSR for logged-in users for now, regardless
        #      of SSR setting. This is mainly to avoid issues with React
        #      SSR hydration.
        if (ssr and not user.is_authenticated) or not csr:
            bundle_path = handler.ssr_bundle_path
            current_user_data = dk_settings.current_user_serializer(user)
            current_user_json = dump_json(current_user_data)
            request_csrf_token = request.META.get("CSRF_COOKIE") or ""

            loader = handler.loader
            if loader is not None:
                loader_kwargs = kwargs.copy()
                data = loader.impl(request, *args, **loader_kwargs)
                data_json = dump_json(data)
            else:
                data_json = ""

            argv = [path, current_user_json, data_json]
            key_parts = [bundle_path] + argv
            key = make_cache_key(*key_parts, request_csrf_token)
            markup = cache.get(key)

            if markup is None:
                log.debug("Generating and caching SSR markup with args: %s", argv)
                markup = run_bundle(bundle_path, argv)

                if "__DJANGOKIT_CSRF_TOKEN__" in markup:
                    log.debug("Injecting CSRF token into SSR markup")
                    csrf_token = get_unmasked_csrf_token(request)

                    if request_csrf_token and csrf_token != request_csrf_token:
                        key = make_cache_key(*key_parts, request_csrf_token)
                        if key in cache:
                            log.debug("Remove cached SSR markup for expired CSRF token")
                            cache.delete(key)

                    key = make_cache_key(*key_parts, csrf_token)
                    markup = markup.replace("__DJANGOKIT_CSRF_TOKEN__", csrf_token)

                cache.set(key, markup, None)
        else:
            # XXX: This is a hack to force the CSRF cookie to *always*
            #      be set in order to avoid 403 errors. This conflicts
            #      with caching. Need to figure out a way to lazily
            #      access the token only when needed.
            get_unmasked_csrf_token(request)
            markup = " ".join(("Loading", dk_settings.title, "-", dk_settings.description))

        context["markup"] = markup
        status = 404 if handler.is_catchall else 200
        return render_template(request, handler.template_name, context, status=status)

    return render
