from functools import lru_cache
from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import View

from ..http import JsonResponse


class ApiView(View):
    """API view.

    Handles API routes.

    """

    api_module = None

    @classmethod
    @lru_cache(maxsize=None)
    def allowed_methods(cls) -> Dict[str, object]:
        """Get allowed methods for API view.

        The allowed methods for an API view are determined by the
        handler functions defined in the configured API module.

        Returns a dict mapping allowed method names to their
        corresponding API handlers.

        .. note::
            This is a class method with a cached return value in order
            to avoid discovering the allowed methods from the API module
            on *every* request.

        """
        if cls.api_module is None:
            raise ImproperlyConfigured(
                "Class attribute api_module must be set for ApiView"
            )
        methods = {}
        has_get = False
        has_head = False
        has_options = False
        for name in dir(cls.api_module):
            if name in View.http_method_names:
                methods[name] = getattr(cls.api_module, name)
                if name == "get":
                    has_get = True
                elif name == "head":
                    has_head = True
                elif name == "options":
                    has_options = True
        if has_get and not has_head:
            methods["head"] = methods["get"]
        if not has_options:
            methods["options"] = cls.options
        return methods

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Dispatch request to API handler.

        API handlers can return one of the following:

        1. A dict or a Model instance, which will be converted to a JSON
           response with a 200 status code.
        2. An HTTP status code (an `int`), which will be converted to an
           empty response with the specified status code *or* to a
           redirect if the status code is 301 or 302.
        3. A status code *and* a dict or Model instance, which will be
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
            302 non-permanent redirects.

        """
        method = request.method.lower()

        if method not in self.allowed_methods:
            return self.http_method_not_allowed(request, *args, **kwargs)

        handler = self.allowed_methods[method]
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
