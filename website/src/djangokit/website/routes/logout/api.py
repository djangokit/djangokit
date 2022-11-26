from django.contrib.auth import logout
from django.shortcuts import redirect


def post(request):
    data = request.POST
    return_path = data.get("from") or "/"
    if not return_path.startswith("/"):
        return 400, f"Bad redirect URL: {return_path}"
    logout(request)
    return_url = request.build_absolute_uri(return_path)
    return redirect(return_url)
