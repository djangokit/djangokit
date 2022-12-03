from django.contrib.auth.decorators import login_required, user_passes_test

# This decorator will cause a redirect-to-login when the user isn't
# authenticated.
#
# NOTE: This is being re-exported here for consistency and convenient
#       access.
require_authenticated = login_required

# These decorators will NOT cause a redirect-to-login when the user
# isn't authenticated. In most cases, you'll probably want to stack
# require_authenticated on top of one of these, like so:
#
#     @auth.require_authenticated
#     @auth.require_superuser
#     def view(request):
#         ...
#
require_staff = user_passes_test(lambda u: u.is_staff or u.is_superuser)
require_superuser = user_passes_test(lambda u: u.is_superuser)


def is_superuser_request(request):
    return request.user.is_authenticated and request.user.is_superuser
