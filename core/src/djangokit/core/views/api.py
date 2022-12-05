from types import ModuleType
from typing import Callable, Dict

from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import View

from ..http import JsonResponse


class ApiView(View):
    """API view.

    Handles API routes.

    """

    api_module: ModuleType = None
    """The API module for this view.
    
    The API module contains the handlers for this view. Each such
    handler should be a function that takes a `request` as its first
    argument plus any URL pattern keyword arguments (the args for API
    handlers are the same as the args for a normal Django view).
    
    Handlers can return a dict, a model instance, or a response object.
    See :meth:`dispatch` below for more details.
    
    """

    allowed_methods: Dict[str, Callable] = None
    """Allowed HTTP methods for API view.
    
    The allowed methods for an API view are determined by the
    handler functions defined in the configured API module.
    
    .. note::
        The allowed methods are configured up front in
        :func:`djangokit.core.routes.discover_routes`. This allows for
        early checks and also avoids having to look up the API handlers
        from the API module on *every* request.
    
    """

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Dispatch request to API handler.

        API handlers can return one of the following:

        1. A dict or a model instance, which will be converted to a JSON
           response with a 200 status code.
        2. An HTTP status code (an `int`), which will be converted to an
           empty response with the specified status code *or* to a
           redirect if the status code is 301 or 302.
        3. A status code *and* a dict or model instance, which will be
           converted to a JSON response with the specified status code
           and data.
        4. A status code *and* a string, which will be converted to a
           response with the specified status code and body  *or* to a
           redirect if the status code is 301 or 302.
        5. None, which will be converted to a 204 No Content response.
        6. A Django response object when more control is needed over the
           response.

        If there's no API handler corresponding to the request's method,
        a 405 response will be returned.

        .. note::
            To redirect, return 301 or 302 and a redirect location.
            E.g., `302, "/login"`. Note that you usually want to use
            302 non-permanent redirects. Note also that trying to
            redirect with data will raise an error (e.g., `302, {}`).

        Raises:
            TypeError:
                When the return value from an API handler isn't valid,
                we raise a `TypeError` because that's a programming
                error.

        """
        method = request.method.lower()
        allowed_methods = self.allowed_methods

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

        if isinstance(result, int):
            status = result
            if status in (301, 302):
                data = "/"
            elif request.accepts("application/json"):
                data = {}
            else:
                data = ""
            result = (status, data)

        if isinstance(result, tuple):
            if len(result) != 2:
                raise TypeError(
                    f"Handler returned tuple with unexpected length {len(result)} "
                    "(expected 2)"
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
            f"Handler returned unexpected object type {type(result)} "
            "(expected dict, Model, int, Tuple[int, dict], "
            "Tuple[int, Model], None or HttpResponse)."
        )
