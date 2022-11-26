from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django.shortcuts import redirect


def post(request: HttpRequest):
    data = request.POST
    username = data["username"]
    password = data["password"]
    return_path = data.get("from") or "/"
    if not return_path.startswith("/"):
        return 400, f"Bad redirect URL: {return_path}"
    user = authenticate(request, username=username, password=password)
    if user is None:
        return 401
    login(request, user)
    return_url = request.build_absolute_uri(return_path)
    return redirect(return_url)
