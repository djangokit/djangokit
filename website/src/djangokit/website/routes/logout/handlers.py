import logging

from django.contrib.auth import logout

from djangokit.core.views.utils import is_site_path

log = logging.getLogger(__name__)


def post(request):
    """User logout endpoint. *Always* redirects."""
    data = request.POST
    redirect_path = data.get("next") or "/"

    logout(request)

    if not is_site_path(redirect_path):
        log.error("Logout redirect URL should be a site path; got %s", redirect_path)
        redirect_path = "/"

    return 302, redirect_path
