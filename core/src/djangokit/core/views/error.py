"""Django error views.

These views render an error page for 400, 403, 404, and 500 responses.
The content depends on the status code.

The error template is `djangokit/error.html`, which assumes your app has
a root layout at `routes/layout.html`.

Customization
-------------

You can customize the error page by adding `djangokit/error.html`
template to your project's `templates` directory. This template will
receive the following context:

* `problem` - :class:`Problem` instance
* `settings` - DjangoKit settings

Example custom error template::

    <div class="alert alert-danger">
        <h1>{% problem.title %}</h1>

        {% if problem.status == 400 %}
            <p>400 content</p>
        {% elif problem.status == 403 %}
            <p>403 content</p>
        {% elif problem.status == 404 %}
            <p>404 content</p>
        {% elif problem.status == 500 %}
            <p>500 content</p>
        {% endif %}
    <div>

.. todo::
    Allow customization of explanation and detail via settings or
    partial templates?

"""

import http
import logging

from django.conf import settings
from django.http import response
from django.template import loader
from django.views import defaults

from ..problem import Problem

log = logging.getLogger(__name__)

TEMPLATE_NAME = "djangokit/error.html"


STATUS_RESPONSE_MAP = {
    400: response.HttpResponseBadRequest,
    403: response.HttpResponseForbidden,
    404: response.HttpResponseNotFound,
    500: response.HttpResponseServerError,
}


STATUS_VIEW_MAP = {
    400: defaults.bad_request,
    403: defaults.permission_denied,
    404: defaults.page_not_found,
    500: defaults.server_error,
}


def bad_request(request, exception, template_name=TEMPLATE_NAME):
    return create_error_response(
        request,
        http.HTTPStatus.BAD_REQUEST,
        detail="Something was wrong with the request.",
        exception=exception,
        template_name=template_name,
    )


def permission_denied(request, exception, template_name=TEMPLATE_NAME):
    return create_error_response(
        request,
        http.HTTPStatus.FORBIDDEN,
        detail="You're not allowed to access this page.",
        exception=exception,
        template_name=template_name,
    )


def page_not_found(request, exception, template_name=TEMPLATE_NAME):
    prefix = f"/{settings.DJANGOKIT.prefix}"
    detail = f"""\
<p>The requested page wasn't found.</p>
<p>Please re-check the address or visit our <a href="{prefix}">home page</a>.</p>"""
    return create_error_response(
        request,
        http.HTTPStatus.NOT_FOUND,
        detail=detail,
        exception=exception,
        template_name=template_name,
    )


def server_error(request, template_name=TEMPLATE_NAME):
    return create_error_response(
        request,
        http.HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="The server ran into an unexpected issue.",
        template_name=template_name,
    )


def create_error_response(
    request,
    status,
    title: str | None = None,
    detail: str | None = None,
    exception: Exception | None = None,
    template_name=TEMPLATE_NAME,
):
    """Create an error response.

    :return:
        A JSON problem details response if the request accepts
        application/json; otherwise, an HTML error page.

    """
    try:
        problem = Problem(
            status,
            title=title,
            detail=detail,
            exception=exception,
        )

        accept = request.META.get("HTTP_ACCEPT", "*/*")

        if accept == "application/json":
            return problem.to_json_response()

        template = loader.get_template(template_name)
        context = {"problem": problem, "settings": settings.DJANGOKIT}
        content = template.render(context, request)
        response_type = STATUS_RESPONSE_MAP.get(status, STATUS_RESPONSE_MAP[500])
        return response_type(content)
    except Exception:
        # XXX: Bail out to Django default handler if rendering fails.
        log.exception(
            "Failed to render error template for %s response: %s.",
            status,
            template_name,
        )
        view = STATUS_VIEW_MAP.get(status, STATUS_VIEW_MAP[500])
        if status in (400, 403, 404):
            return view(request, exception)
        return view(request)
