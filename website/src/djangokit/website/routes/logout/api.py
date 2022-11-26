from django.contrib.auth import logout
from django.shortcuts import redirect


def post(request):
    logout(request)
    return redirect("/")
