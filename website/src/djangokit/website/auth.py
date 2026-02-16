from django.contrib.auth.decorators import login_required, user_passes_test

# This decorator will cause a redirect-to-login when the user isn't
# authenticated.
#
# NOTE: This is being re-exported here for consistency and convenient
#       access.
require_authenticated = login_required

# These decorators will cause a redirect-to-login when the user isn't
# authenticated.
require_staff = user_passes_test(
    lambda u: user_passes_test(require_authenticated) and (u.is_staff or u.is_superuser)
)
require_superuser = user_passes_test(
    lambda u: user_passes_test(require_authenticated) and u.is_superuser
)
