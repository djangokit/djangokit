from django.contrib.auth import authenticate, login
from django.shortcuts import redirect


def post(request):
    data = request.POST
    username = data["username"]
    password = data["password"]
    user = authenticate(request, username=username, password=password)
    if user is None:
        return 401
    login(request, user)
    return redirect("/")
