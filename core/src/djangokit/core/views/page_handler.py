import logging
from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render as render_template

from .handler import Handler, Impl

log = logging.getLogger(__name__)


@dataclass
class PageHandler(Handler):
    """Handler for rendering pages.

    Note that this only used for GET and HEAD requests.

    """

    impl: Impl = field(init=False)
    method: str = "get"
    path: str = ""

    template_name: str = "djangokit/app.html"
    """Template used to render page."""

    loader: Optional[Handler] = None
    """The handler that is the loader for this view."""

    def __post_init__(self):
        self.impl = make_impl(self)
        super().__post_init__()


def make_impl(handler: PageHandler) -> Impl:
    loader = handler.loader
    template_name = handler.template_name

    def impl(request: HttpRequest, *args, **kwargs):
        """Render page template."""
        if loader:
            result = loader.impl(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                # TODO: Should this throw?
                log.error("Loader returned HttpResponse; cannot render page template")
                return result
            status, data = loader.get_status_and_data_for_result(request, result)
        else:
            status, data = 200, None

        return render_template(
            request,
            template_name,
            status=status,
            context={
                "django_settings": settings,
                "settings": settings.DJANGOKIT,
                "data": data,
            },
        )

    return impl
