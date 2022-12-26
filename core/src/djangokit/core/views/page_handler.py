import json
import logging
from dataclasses import dataclass, field
from hashlib import sha1
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.middleware import csrf
from django.shortcuts import render as render_template

from ..build import run_bundle
from ..serializers import JsonEncoder
from .handler import Handler, Impl

log = logging.getLogger(__name__)


@dataclass
class PageHandler(Handler):
    """Handler for rendering pages."""

    impl: Impl = field(init=False)
    method: str = "get"
    path: str = ""

    template_name: str = "djangokit/app.html"
    """Template used to render page for both CSR & SSR."""

    ssr_bundle_path: Path = Path()
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

        return render_template(request, handler.template_name, context)

    return render
