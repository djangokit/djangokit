import logging
from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings
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
        self.impl = make_render(self)
        super().__post_init__()


def make_render(handler):
    def render(request, *args, **kwargs):
        """Render page template."""
        if handler.loader:
            data = handler.loader.impl(request, *args, **kwargs)
        else:
            data = None
        return render_template(
            request,
            handler.template_name,
            context={
                "django_settings": settings,
                "settings": settings.DJANGOKIT,
                "data": data,
            },
        )

    return render
