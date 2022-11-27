from django.http import HttpRequest


def make_request(path="/", path_info=None):
    """Make a request object with the specified path."""
    request = HttpRequest()
    request.path = path
    request.path_info = path_info or path
    return request
