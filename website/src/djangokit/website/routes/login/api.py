import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpRequest

from djangokit.core.views.utils import is_site_path


log = logging.getLogger(__name__)


def post(request: HttpRequest):
    """User login endpoint. *Always* redirects."""
    data = request.POST
    username = data["username"]
    password = data["password"]
    redirect_path = data.get("next") or "/"

    if not is_site_path(redirect_path):
        log.error("Login redirect URL should be a site path; got %s", redirect_path)
        redirect_path = "/"

    user = authenticate(request, username=username, password=password)
    if user is None:
        # Authentication failed.
        redirect_path = settings.LOGIN_URL
    else:
        # Authentication succeeded.
        login(request, user)

    return 302, redirect_path
