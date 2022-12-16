"""Django error views.

These views render error pages that users should rarely to never see for
400, 403, 404, and 500 responses.

In a default DjangoKit setup, 404 responses will be handled at the UI
level by a catchall route.

Customization
-------------

You can customize these error pages by adding a `djangokit/error.html`
template to your project's `templates` directory. This template will
receive the following context:

* `exception` - The underlying exception, if available
* `settings` - DjangoKit settings
* `status_code` - HTTP status code of response
* `explanation` - Short explanation of error (e.g., "Not Found")
* `detail` - More detail about the error

To customize the explanation and detail messages, you can ignore the
values passed in the template context and do this in your custom error
template::

    {% if status_code == 400 %}
        <p>400 content</p>
    {% elif status_code == 403 %}
        <p>403 content</p>
    {% elif status_code == 404 %}
        <p>404 content</p>
    {% elif status_code == 500 %}
        <p>500 content</p>
    {% endif %}

.. todo::
    Allow customization of explanation and detail via settings or
    partial templates?

"""
import logging

from django.conf import settings
from django.http import response
from django.template import loader
from django.views import defaults

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
    return generic_error(
        request,
        exception,
        400,
        "Bad Request",
        "Something was wrong with the request.",
        template_name,
    )


def permission_denied(request, exception, template_name=TEMPLATE_NAME):
    return generic_error(
        request,
        exception,
        403,
        "Forbidden",
        "You're not allowed to access this page.",
        template_name,
    )


def page_not_found(request, exception, template_name=TEMPLATE_NAME):
    return generic_error(
        request,
        exception,
        404,
        "Not Found",
        "not found"
        "<p>The requested page wasn't found.</p>"
        '<p>Please re-check the address or visit our <a href="/">home page</a>.</p>',
        template_name,
    )


def server_error(request, template_name=TEMPLATE_NAME):
    return generic_error(
        request,
        None,
        500,
        "Internal Server Error",
        "The server ran into an unexpected issue.",
        template_name,
    )


def generic_error(
    request,
    exception,
    status_code,
    explanation=None,
    detail=None,
    template_name=TEMPLATE_NAME,
):
    try:
        template = loader.get_template(template_name)
        context = {
            "exception": exception,
            "settings": settings.DJANGOKIT,
            "status_code": status_code,
            "explanation": explanation,
            "detail": detail,
        }
        content = template.render(context, request)
        response_type = STATUS_RESPONSE_MAP.get(status_code, STATUS_RESPONSE_MAP[500])
        return response_type(content)
    except Exception:
        # XXX: Bail out to Django default handler if rendering fails.
        log.exception(
            "Failed to render error template for %s response: %s.",
            status_code,
            template_name,
        )
        view = STATUS_VIEW_MAP.get(status_code, STATUS_VIEW_MAP[500])
        if status_code in (400, 403, 404):
            return view(request, exception)
        return view(request)
